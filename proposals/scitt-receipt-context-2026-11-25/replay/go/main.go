// Replay the fixed two-leaf A1 corpus using the supplied fixture directory.
package main

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/fxamacker/cbor/v2"
	cose "github.com/veraison/go-cose"
)

type signedRecord struct{ Body, Signature string }
type bundle struct {
	Service   string
	Statement string
	Sibling   string `json:"sibling_statement"`
	Receipts  map[string]string
	Records   map[string]signedRecord
}
type view struct{ Rules, Keys, Receipts []string }
type trust struct {
	Service   string
	Archive   string `json:"archive_public_key"`
	Authority string `json:"key_authority_public_key"`
	Issuer    string `json:"issuer_public_key"`
	Views     map[string]view
}
type record struct {
	Kind, Service, Rule, Epoch, Preprocessing, Kid, Status string
	Entry                                                  string `json:"entry_sha256"`
	Receipt                                                string `json:"receipt_sha256"`
	Key                                                    string `json:"public_key"`
}

// These are assertions on the checked-in corpus. An unsupported fixture is an
// execution error. The experiment has separate results for absent key history
// and competing authenticated rule records.
func require(ok bool, why string) {
	if !ok {
		log.Fatal(why)
	}
}
func check(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
func unhex(s string) []byte {
	b, err := hex.DecodeString(s)
	check(err)
	return b
}
func key(s string) ed25519.PublicKey {
	b := unhex(s)
	require(len(b) == ed25519.PublicKeySize, "expected an Ed25519 public key")
	return ed25519.PublicKey(b)
}
func readJSON(file string, target any) {
	b, err := os.ReadFile(file)
	check(err)
	check(json.Unmarshal(b, target))
}
func hash(parts ...[]byte) []byte {
	h := sha256.New()
	for _, p := range parts {
		h.Write(p)
	}
	return h.Sum(nil)
}
func digest(b []byte) string { return hex.EncodeToString(hash(b)) }

type header struct {
	Algorithm int            `cbor:"1,keyasint"`
	Kid       []byte         `cbor:"4,keyasint"`
	Claims    map[int]string `cbor:"15,keyasint"`
	VDS       int            `cbor:"395,keyasint"`
}
type envelope struct {
	msg    cose.Sign1Message
	fields [4]cbor.RawMessage
	header header
}

func decode(wire []byte) envelope {
	require(bytes.HasPrefix(wire, []byte{0xd2, 0x84}), "expected tagged definite four-element COSE_Sign1")
	var e envelope
	check(e.msg.UnmarshalCBOR(wire))
	check(cbor.Unmarshal(wire[1:], &e.fields))
	var protected []byte
	check(cbor.Unmarshal(e.fields[0], &protected))
	check(cbor.Unmarshal(protected, &e.header))
	require(e.header.Algorithm == -8 && len(e.header.Kid) > 0 && e.header.Claims[1] != "" && e.header.Claims[2] != "", "incomplete protected fixture headers")
	return e
}

func verify(msg cose.Sign1Message, k ed25519.PublicKey) {
	v, err := cose.NewVerifier(cose.AlgorithmEdDSA, k)
	check(err)
	check(msg.Verify(nil, v))
}

func entry(wire []byte, issuer string, subject string) []byte {
	e := decode(wire)
	require(e.header.Claims[1] == "https://issuer.example" && e.header.Claims[2] == subject && string(e.header.Kid) == "ISSUER", "unexpected issuer or subject in fixed fixture")
	verify(e.msg, key(issuer))
	var out bytes.Buffer
	out.Write([]byte{0xd2, 0x84})
	for i, field := range e.fields {
		if i == 1 {
			out.WriteByte(0xa0)
			continue
		}
		require(len(field) > 0 && field[0]>>5 == 2 && field[0]&31 != 31, "expected a definite byte string")
		out.Write(field) // Keep complete encoded elements, including their original lengths.
	}
	return out.Bytes()
}

func (b bundle) authenticated(id, authority, kind string) record {
	s, ok := b.Records[id]
	require(ok, "missing record "+id)
	body := unhex(s.Body)
	require(ed25519.Verify(key(authority), body, unhex(s.Signature)), "invalid signed record "+id)
	var r record
	check(json.Unmarshal(body, &r))
	require(r.Kind == kind && r.Service == b.Service && r.Epoch != "", "wrong authority scope for "+id)
	return r
}

type proof struct {
	_           struct{} `cbor:",toarray"`
	Size, Index uint64
	Path        [][]byte
}

func verifyInclusion(e envelope, leaf, sibling []byte, signingKey string) []byte {
	require(e.msg.Payload == nil && e.header.VDS == 1, "expected detached RFC9162_SHA256 receipt")
	var headers map[int]cbor.RawMessage
	check(cbor.Unmarshal(e.fields[1], &headers))
	var proofs map[int][][]byte
	check(cbor.Unmarshal(headers[396], &proofs))
	require(len(proofs[-1]) == 1, "expected one encoded inclusion proof")
	var proof proof
	check(cbor.Unmarshal(proofs[-1][0], &proof))
	require(proof.Size == 2 && proof.Index == 0 && len(proof.Path) == 1, "outside fixed two-leaf fixture shape")
	require(bytes.Equal(proof.Path[0], sibling), "sibling does not match second signed entry")
	root := hash([]byte{1}, leaf, proof.Path[0])
	e.msg.Payload = root // go-cose verifies the original protected bytes and the detached root.
	verify(e.msg, key(signingKey))
	return root
}

func main() {
	log.SetFlags(0)
	if len(os.Args) != 2 {
		log.Fatal("usage: go run . <replay-directory>")
	}
	var b bundle
	var t trust
	readJSON(filepath.Join(os.Args[1], "bundle.json"), &b)
	readJSON(filepath.Join(os.Args[1], "trust.json"), &t)
	require(b.Service != "" && t.Service == b.Service, "service is not locally authorized")
	const subject = "urn:example:fixture:primary"
	e := entry(unhex(b.Statement), t.Issuer, subject)
	leaf := hash([]byte{0}, e)
	sibling := hash([]byte{0}, entry(unhex(b.Sibling), t.Issuer, "urn:example:fixture:sibling"))
	entryID := digest(e)
	receiptIDs := map[string]string{}
	for name, wire := range b.Receipts {
		receiptIDs[name] = digest(unhex(wire))
	}
	require(len(receiptIDs) == 2 && receiptIDs["K1"] != "" && receiptIDs["K2"] != "" && receiptIDs["K1"] != receiptIDs["K2"], "expected two distinct receipts")
	results := map[string]map[string]string{}
	details := map[string]map[string]map[string]string{}
	var verifiedRoot []byte
	for name, v := range t.Views {
		rules := []record{}
		for _, id := range v.Rules {
			r := b.authenticated(id, t.Archive, "entry-rule")
			if r.Entry == entryID && r.Preprocessing == "restricted-E-v1" {
				rules = append(rules, r)
			}
		}
		cases := map[string]string{}
		details[name] = map[string]map[string]string{}
		for _, id := range v.Receipts {
			detail := map[string]string{}
			details[name][id] = detail
			wire, ok := b.Receipts[id]
			require(ok, "missing receipt "+id)
			receipt := decode(unhex(wire))
			require(receipt.header.Claims[1] == t.Service && receipt.header.Claims[2] == subject && string(receipt.header.Kid) == id, "unexpected receipt identity")
			if len(rules) > 1 {
				cases[id] = "context_ambiguous_rule"
				continue
			}
			require(len(rules) == 1 && rules[0].Rule == "A1", "outside supported unambiguous A1 context")
			detail["rule"], detail["rule_epoch"] = rules[0].Rule, rules[0].Epoch
			var signingKey string
			for _, rid := range v.Keys {
				k := b.authenticated(rid, t.Authority, "receipt-key")
				require(k.Status == "retired" || k.Status == "current", "unsupported fixture key status")
				if k.Kid == string(receipt.header.Kid) && k.Receipt == receiptIDs[id] {
					require(signingKey == "", "ambiguous key assertion")
					signingKey = k.Key
					detail["key_epoch"], detail["key_status"] = k.Epoch, k.Status
				}
			}
			if signingKey == "" {
				cases[id] = "context_insufficient_key"
				continue
			}
			root := verifyInclusion(receipt, leaf, sibling, signingKey)
			require(verifiedRoot == nil || bytes.Equal(root, verifiedRoot), "reissued root disagreement")
			verifiedRoot = root
			cases[id] = "verified"
			detail["claim"] = "inclusion under service-signed root"
		}
		results[name] = cases
	}
	require(verifiedRoot != nil, "no verified receipt")
	report := map[string]any{"entry_sha256": entryID, "leaf_sha256": hex.EncodeToString(leaf),
		"root_sha256": hex.EncodeToString(verifiedRoot), "receipt_sha256": receiptIDs, "cases": results, "details": details,
		"source_completeness": "unassessed", "history_consistency": "unassessed", "issuance_time": "unassessed",
		"position_and_size": "unassessed", "local_vcp_batch_integrity": "unassessed"}
	out, err := json.MarshalIndent(report, "", "  ")
	check(err)
	fmt.Println(string(out))
}
