# MIN-43 insight: connector visibility is not Darwin authority

The useful boundary is between an in-Chat connector summary and an API
credential/runtime capability on Darwin. Treating visibility as authorization
would silently invent access, freshness, scheduler control, and quota
ownership. The registry therefore makes access state, source-of-truth, consent
subject, and verification evidence independent fields, with additional Gmail
accounts requiring their own consent record.
