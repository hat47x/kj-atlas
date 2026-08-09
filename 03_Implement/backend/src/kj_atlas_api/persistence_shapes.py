from dataclasses import dataclass
from enum import Enum


class DataShape(str, Enum):
    IDENTIFIER = "identifier"
    BOUNDED_TEXT = "bounded_text"
    CONTENT_OBJECT = "content_object"


@dataclass(frozen=True)
class PersistentTextSpec:
    shape: DataShape
    proposed_max_chars: int | None
    rationale: str


def _identifier(max_chars: int, rationale: str) -> PersistentTextSpec:
    return PersistentTextSpec(DataShape.IDENTIFIER, max_chars, rationale)


def _bounded(max_chars: int, rationale: str) -> PersistentTextSpec:
    return PersistentTextSpec(DataShape.BOUNDED_TEXT, max_chars, rationale)


CONTENT_OBJECT = PersistentTextSpec(
    DataShape.CONTENT_OBJECT,
    None,
    "opaque versioned content; enforce byte-size policy separately from DB column length",
)
INTERNAL_ID = _identifier(128, "application identifier and composite-index component")
EXTERNAL_ID = _identifier(512, "externally issued identifier with a product acceptance bound")
VERSION_ID = _identifier(128, "version, digest prefix, or policy identifier")
TIMESTAMP = _bounded(40, "canonical RFC 3339 timestamp with timezone and fractional seconds")
STATE = _bounded(32, "closed-set lifecycle, action, decision, or protocol discriminator")


# This catalog is intentionally explicit. A coverage test rejects every new SQLAlchemy
# Text column until its product meaning is classified here.
PERSISTENT_TEXT_SPECS: dict[str, PersistentTextSpec] = {
    "identity_providers.id": INTERNAL_ID,
    "identity_providers.issuer": _bounded(2048, "OIDC issuer URI"),
    "identity_providers.audience": _bounded(512, "OIDC audience value"),
    "identity_providers.lifecycle_state": STATE,
    "identity_providers.protocol": STATE,
    "identity_providers.jwks_uri": _bounded(2048, "JWKS URI"),
    "identity_providers.created_at": TIMESTAMP,
    "identity_providers.updated_at": TIMESTAMP,
    "tenants.id": INTERNAL_ID,
    "tenants.display_name": _bounded(255, "human-readable tenant label"),
    "tenants.lifecycle_state": STATE,
    "tenants.created_at": TIMESTAMP,
    "tenants.updated_at": TIMESTAMP,
    "users.id": INTERNAL_ID,
    "users.display_name": _bounded(255, "human-readable user label"),
    "users.email": _bounded(320, "email address acceptance bound"),
    "users.lifecycle_state": STATE,
    "users.created_at": TIMESTAMP,
    "users.updated_at": TIMESTAMP,
    "documents.tenant_id": INTERNAL_ID,
    "documents.id": INTERNAL_ID,
    "documents.updated_at": TIMESTAMP,
    "documents.payload_json": CONTENT_OBJECT,
    "inquiry_bundle_deletion_audit_events.event_id": INTERNAL_ID,
    "inquiry_bundle_deletion_audit_events.tenant_id": INTERNAL_ID,
    "inquiry_bundle_deletion_audit_events.journey_id": _identifier(
        256, "journey identifier; matches the existing API acceptance contract"
    ),
    "inquiry_bundle_deletion_audit_events.principal_id": EXTERNAL_ID,
    "inquiry_bundle_deletion_audit_events.action": STATE,
    "inquiry_bundle_deletion_audit_events.outcome": STATE,
    "inquiry_bundle_deletion_audit_events.occurred_at": TIMESTAMP,
    "inquiry_bundles.tenant_id": INTERNAL_ID,
    "inquiry_bundles.journey_id": _identifier(
        256, "journey identifier; matches the existing API acceptance contract"
    ),
    "inquiry_bundles.payload_json": CONTENT_OBJECT,
    "inquiry_bundles.updated_at": TIMESTAMP,
    "tenant_identity_providers.tenant_id": INTERNAL_ID,
    "tenant_identity_providers.identity_provider_id": INTERNAL_ID,
    "tenant_identity_providers.external_tenant_ref": EXTERNAL_ID,
    "tenant_identity_providers.lifecycle_state": STATE,
    "tenant_identity_providers.created_at": TIMESTAMP,
    "tenant_identity_providers.updated_at": TIMESTAMP,
    "tenant_memberships.tenant_id": INTERNAL_ID,
    "tenant_memberships.user_id": INTERNAL_ID,
    "tenant_memberships.lifecycle_state": STATE,
    "tenant_memberships.created_at": TIMESTAMP,
    "tenant_memberships.updated_at": TIMESTAMP,
    "user_identities.user_id": INTERNAL_ID,
    "user_identities.provider": _bounded(64, "normalized identity-provider discriminator"),
    "user_identities.external_uid": EXTERNAL_ID,
    "user_identities.identity_provider_id": INTERNAL_ID,
    "user_identities.subject": EXTERNAL_ID,
    "user_identities.created_at": TIMESTAMP,
    "document_access_admin_audit_events.event_id": INTERNAL_ID,
    "document_access_admin_audit_events.tenant_id": INTERNAL_ID,
    "document_access_admin_audit_events.principal_id": EXTERNAL_ID,
    "document_access_admin_audit_events.doc_id": INTERNAL_ID,
    "document_access_admin_audit_events.action": STATE,
    "document_access_admin_audit_events.decision": STATE,
    "document_access_admin_audit_events.policy_version": VERSION_ID,
    "document_access_admin_audit_events.capability_version": VERSION_ID,
    "document_access_admin_audit_events.correlation_id": INTERNAL_ID,
    "document_access_admin_audit_events.occurred_at": TIMESTAMP,
    "document_access_metadata.tenant_id": INTERNAL_ID,
    "document_access_metadata.doc_id": INTERNAL_ID,
    "document_access_metadata.visibility": STATE,
    "document_access_metadata.policy_binding_id": EXTERNAL_ID,
    "document_access_metadata.policy_version": VERSION_ID,
    "document_access_metadata.updated_at": TIMESTAMP,
    "merge_decision_logs.tenant_id": INTERNAL_ID,
    "merge_decision_logs.doc_id": INTERNAL_ID,
    "merge_decision_logs.decision_id": INTERNAL_ID,
    "merge_decision_logs.group_id": INTERNAL_ID,
    "merge_decision_logs.snapshot_version": VERSION_ID,
    "merge_decision_logs.decided_at": TIMESTAMP,
    "merge_decision_logs.payload_json": CONTENT_OBJECT,
}
