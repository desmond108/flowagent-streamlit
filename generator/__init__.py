"""FlowAgent output generator.

Deterministic renderer that turns an authored SopPackage (see sop_data/) into
the six FlowAgent deliverables as PDF:

  a. Process flow  -> swimlane deck + hierarchy deck
  b. Fit-gap       -> fit-gap analysis deck
  c. Optimised flow-> optimised swimlane deck + optimised hierarchy deck
  d. Optimised SOP -> Word-style A4 document

Rendering is HTML/CSS -> PDF via headless Google Chrome (see render.py).
"""
