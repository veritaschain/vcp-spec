# VCP Examples

Quick start examples for VeritasChain Protocol.

## 🐍 Python

```bash
cd python
pip install httpx
export VCP_API_KEY="your-api-key"
python quickstart.py
```

## 📘 TypeScript

```bash
cd typescript
npm init -y
npm install typescript ts-node @types/node
export VCP_API_KEY="your-api-key"
npx ts-node quickstart.ts
```

## 🔧 curl

No installation required:

```bash
# System status (no auth)
curl https://explorer.veritaschain.org/api/v1/system/status | jq

# Search events
curl -H "Authorization: Bearer $VCP_API_KEY" \
  "https://explorer.veritaschain.org/api/v1/events?limit=5" | jq
```

## 📋 Get API Key

See the [Explorer API page](https://veritaschain.org/vcp/explorer-api/) (no self-service registration page is currently published).

The quickstart Merkle checks compare an API-supplied path with an API-supplied
root using the VCP v1.2 §6.2 example construction, not RFC 6962 (see
[Known issues](../README.md#-known-issues-in-v12-informative), P3). For an RFC 6962
verifier, see [veritaschain/vcp-sdk](https://github.com/veritaschain/vcp-sdk)
(pre-release, first-party).

## 📖 More Information

- [Quick Start Guide](../docs/QUICKSTART.md)
- [VCP Specification v1.2](../spec/v1.2/VCP-Specification-v1_2_en.md)
- [SDK Specification](https://github.com/veritaschain/vcp-sdk-spec)
