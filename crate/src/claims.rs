//! Epistemic Typing and Cryptographic Claim Receipts for AMDE.
//! Adheres strictly to PRD-26 / RP-002 taxonomy:
//! - Transformation kinds: ISO, ADJOINT, LOSSY, APPROXIMATE
//! - Epistemic statuses: THEOREM, FORMALIZATION, LEMMA_TARGET, CONJECTURE, EXPERIMENT, ANALOGY

use crate::math_core::Sha256;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransformationKind {
    Iso,
    Adjoint,
    Lossy,
    Approximate,
}

impl TransformationKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Iso => "ISO",
            Self::Adjoint => "ADJOINT",
            Self::Lossy => "LOSSY",
            Self::Approximate => "APPROXIMATE",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EpistemicStatus {
    Theorem,
    Formalization,
    LemmaTarget,
    Conjecture,
    Experiment,
    Analogy,
}

impl EpistemicStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Theorem => "THEOREM",
            Self::Formalization => "FORMALIZATION",
            Self::LemmaTarget => "LEMMA_TARGET",
            Self::Conjecture => "CONJECTURE",
            Self::Experiment => "EXPERIMENT",
            Self::Analogy => "ANALOGY",
        }
    }
}

#[derive(Debug, Clone)]
pub struct ClaimReceipt {
    pub claim_id: String,
    pub title: String,
    pub transformation_kind: TransformationKind,
    pub epistemic_status: EpistemicStatus,
    pub source_representation: String,
    pub target_representation: String,
    pub input_value: String,
    pub output_value: String,
    pub delta_i: f64,
    pub metric_error: f64,
    pub tolerance: f64,
    pub verified: bool,
    pub notes: String,
    pub sha256_hash: String,
}

impl ClaimReceipt {
    pub fn new(
        claim_id: &str,
        title: &str,
        kind: TransformationKind,
        status: EpistemicStatus,
        source: &str,
        target: &str,
        input: &str,
        output: &str,
        delta_i: f64,
        metric_error: f64,
        tolerance: f64,
        verified: bool,
        notes: &str,
    ) -> Self {
        // Construct canonical preimage for cryptographic hashing
        let payload = format!(
            "id={}|kind={}|status={}|src={}|tgt={}|in={}|out={}|dI={:.6}|err={:.8}|tol={:.8}|ver={}|notes={}",
            claim_id,
            kind.as_str(),
            status.as_str(),
            source,
            target,
            input,
            output,
            delta_i,
            metric_error,
            tolerance,
            verified,
            notes
        );
        let sha256_hash = Sha256::digest_hex(payload.as_bytes());

        Self {
            claim_id: claim_id.to_string(),
            title: title.to_string(),
            transformation_kind: kind,
            epistemic_status: status,
            source_representation: source.to_string(),
            target_representation: target.to_string(),
            input_value: input.to_string(),
            output_value: output.to_string(),
            delta_i,
            metric_error,
            tolerance,
            verified,
            notes: notes.to_string(),
            sha256_hash,
        }
    }

    pub fn to_json(&self) -> String {
        format!(
            "{{\"claim_id\":\"{}\",\"title\":\"{}\",\"transformation_kind\":\"{}\",\"epistemic_status\":\"{}\",\"source\":\"{}\",\"target\":\"{}\",\"input\":\"{}\",\"output\":\"{}\",\"delta_i\":{:.6},\"metric_error\":{:.8},\"tolerance\":{:.8},\"verified\":{},\"notes\":\"{}\",\"sha256\":\"{}\"}}",
            self.claim_id,
            escape_json(&self.title),
            self.transformation_kind.as_str(),
            self.epistemic_status.as_str(),
            escape_json(&self.source_representation),
            escape_json(&self.target_representation),
            escape_json(&self.input_value),
            escape_json(&self.output_value),
            self.delta_i,
            self.metric_error,
            self.tolerance,
            self.verified,
            escape_json(&self.notes),
            self.sha256_hash
        )
    }
}

pub fn escape_json(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 16);
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            _ => out.push(c),
        }
    }
    out
}
