## Relationship Manager

### Status
Accepted

### Date accepted
2025-10-28

### Context
There is a difference in how relationships are handled between our Core (meldingen-core) and our FastAPI implementation (meldingen). 
Consider the Many-To-One relation between Melding and Classification. In meldingen-core a Melding's classification can be accessed directly via a property (melding.classification), while in Meldingen the classification needs to be fetched separately due to lazy loading settings (melding.awaitable_attrs.classification). 

Now, for fetching a relation one can also use a query: `classification_repository.find_by_melding_id(melding.id)`. 
This works for fetching relationships, but there is not a good way to add the relationship to the Melding object itself that works similarly in the core and implementation. 

In the core you can simply assign the relationship directly: `melding.classification = classification`.
In the implementation however, you would need to assign it to the awaitable_attrs: `melding.awaitable_attrs.classification = classification`.
Or in the case of a Many-To-Many relationship, you would need to append to a list: `melding.awaitable_attrs.assets.append(asset)`.

For that reason we have introduced a RelationshipManager as an abstract to handle relationship fetching and assignment in a consistent way.
You can find the definition in [managers.py](../../meldingen_core/managers.py).

The class can be instantiated in our FastAPI implemementation as follows:

```python
def melding_classification_relationship_manager(
    repository: Annotated[MeldingRepository, Depends(melding_repository)],
) -> RelationshipManager[Melding, Asset]:
    return RelationshipManager(repository, get_related=lambda melding: melding.awaitable_attrs.classification)
``` 

### Consequences
- Makes it possible to define more logic in the core instead of the implementation

### Alternatives Considered

- Eagerly loading all relationships in Meldingen to match meldingen-core behavior. This doesn't align with our API design principle where we prefer to fetch related data only when necessary.

### References
...
