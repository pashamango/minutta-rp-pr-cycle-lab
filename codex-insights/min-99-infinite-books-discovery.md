# MIN-99 insight: provenance must precede narrative generation

For reader-local self-writing books, the first hard boundary is not model
quality but corpus provenance. A narrative loop cannot be reproducible or
safe until every source has immutable coordinates, license/usage status, and a
content manifest. The project should therefore make source intake a blocking
gate before mining, semantic indexing, or WASM execution. This also keeps
content-addressing distinct from lazy inference: a hash identifies an input,
but does not prove that the computation producing a chapter was performed or
replayed.
