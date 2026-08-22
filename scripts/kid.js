const { createHash } = require('crypto');
const pub = process.argv[2];
if (!pub) { console.error('usage: node scripts/kid.js <hexPublicKey>'); process.exit(1); }
const rawB = Buffer.from(pub, 'hex');
const jwk = Buffer.from(JSON.stringify({crv:'Ed25519',kty:'OKP',x:Buffer.from(rawB).toString('base64url')}));
const thumb = createHash('sha256').update(jwk).digest('base64url');
console.log(thumb);
