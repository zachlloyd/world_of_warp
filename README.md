# World of Warp

Server simulation for the World of Warp environment.

## Structure

```
services/sector-sim/
  data/catalog.json    # Primitive definitions catalog
  schema/              # JSON schemas for validation
  sim/                 # Simulation tick handlers
  render/              # Render metadata and fallback logic
  tests/               # Test suite
primitives/backlog/    # Primitive spec documents
```

## Running Tests

```bash
cd services/sector-sim
pip install jsonschema pytest
pytest tests/ -v
```
