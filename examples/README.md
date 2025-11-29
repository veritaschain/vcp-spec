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

1. Go to [veritaschain.org/register](https://veritaschain.org/register)
2. Create account
3. Copy API key

## 📖 More Information

- [Quick Start Guide](../docs/QUICKSTART.md)
- [VCP Specification](../VCP-Specification-v1_0_en.md)
- [SDK Specification](https://github.com/veritaschain/vcp-sdk-spec)
