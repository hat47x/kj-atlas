from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_REL = "01_Plans/issues/issue-PGM-ITER-05-03-cross-tenant-guest-admission-primitive-requirements.md"
NEW_REL = "01_Plans/issues/done/issue-PGM-ITER-05-03-cross-tenant-guest-admission-primitive-requirements.md"
OLD = ROOT / OLD_REL
NEW = ROOT / NEW_REL

text = OLD.read_text(encoding="utf-8")
if "- [ ] AC-" in text:
    raise RuntimeError("PGM-ITER-05-03 still has incomplete acceptance criteria")
if text.count("- [x] AC-") != 4:
    raise RuntimeError("expected exactly four completed acceptance criteria")
if "- Status: Open" not in text:
    raise RuntimeError("expected active issue Status: Open")
text = text.replace("- Status: Open", "- Status: Done", 1)
text = text.replace(
    "- R2c verification: branch CIの実署名JWT + guest redeem/read/revoke + trusted-auth regressions + docs/diff hygieneを参照",
    "- R2c verification: GitHub Actions run `34049094121`（86 tests + 実署名RS256 guest redeem/read/revoke + trusted-auth/JWKS regressions + docs/diff hygiene）",
    1,
)
closeout = '''## Final closeout（2026-09-07）

PGM-ITER-05-03は、Accepted ADR-0080で定めたD1〜D4をR1〜R2cで実装・integration verificationし、AC-1〜AC-4を満たしたためDoneとする。

- R1（PR #3018 / merge `cab0c3451bb6950e457c86faac17b384101a1a5c`）で、guest principalとexact document grantをmembershipから分離し、既定拒否・既定0件・host単独revoke・PostgreSQL FORCE RLSを固定した。
- R2aでserver-owned guest sessionからexact document readへ接続し、same-tenant未付与/cross-tenantを404、writeを403、grant/principal revokeを次requestへ即時反映した。
- R2b（PR #3039）でhost-bound one-time redeem stateからverified guest identityをbindし、principal activation・state consume・guest session発行を同一transactionへ固定した。
- R2c（PR #3041 / merge `c40f1c54c87fabc0e34578948dca3a754ec93914`）でconfigured OIDC/JWKSの実署名検証をproduction runtimeへ接続した。実署名RS256 integrationでも`TenantIdentityProviderRow`・`UserIdentityRow`・`TenantMembershipRow`を作らず、guest-only identity→session→exact grant read→host revokeまでを固定した。

Doneは「任意の外部IdP/OAuth方式をkj-atlas自身が直接実装済み」という意味ではない。provider固有redirect UI、authorization-code exchange、nonce/PKCE、opaque token用adapter、guest logout、将来のguest writeは本issueの受入条件外であり、必要になった時点で別issueとして扱う。受入先tenantのIdP trustをguestへ流用しないこと、guest principalだけからtenant-wide document visibilityを導出しないことはDone後も不変条件とする。

'''
marker = "## 検証\n"
if marker not in text:
    raise RuntimeError("verification heading not found")
text = text.replace(marker, closeout + marker, 1)
NEW.parent.mkdir(parents=True, exist_ok=True)
NEW.write_text(text, encoding="utf-8")
OLD.unlink()

suffixes = {".md", ".html", ".json", ".py", ".yml", ".yaml", ".txt"}
changed = []
replacements = 0
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in suffixes:
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    count = content.count(OLD_REL)
    if count:
        path.write_text(content.replace(OLD_REL, NEW_REL), encoding="utf-8")
        replacements += count
        changed.append(str(path.relative_to(ROOT)))

print(f"closeout moved issue and updated {replacements} canonical path reference(s)")
for path in changed:
    print(path)
