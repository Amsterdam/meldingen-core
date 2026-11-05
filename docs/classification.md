# Classification

Classification connects a melding's text to a configured `Classification` record. The core owns the selection flow, while classifier adapters provide the classification name and the application supplies the repository and concrete adapters.

## Classifier flow

`Classifier` is initialized with an ordered list of `BaseClassifierAdapter` instances, a `BaseClassificationRepository`, and the name of a default classification. Each adapter is an asynchronous callable that accepts the melding text and returns a classification name (`str`) or `None`.

When called with text, the classifier:

1. Calls adapters in their configured order, one at a time.
2. Continues after an adapter returns `None` or raises an exception. The first non-`None` name stops the adapter loop.
3. Looks up that name with `BaseClassificationRepository.find_by_name`.
4. Uses the configured default classification if every adapter failed or returned `None`, or if the returned name is not found.
5. Returns a tuple: `(classification, adapter_result)`. `adapter_result` is the first non-`None` name produced by an adapter, even when that name cannot be looked up and the default classification is used. It is `None` when no adapter produced a name.

The configured default must exist in the repository. Errors looking up that default (or repository errors other than `NotFoundException` while looking up an adapter result) propagate to the caller.

```python
class ExampleAdapter(BaseClassifierAdapter):
    async def __call__(self, text: str) -> str | None:
        # Return a configured classification name, or None when this adapter has no result.
        ...


classifier = Classifier(
    adapters=[ExampleAdapter("example")],
    repository=classification_repository,
    classification_default_name="general",
)
classification, adapter_result = await classifier(melding_text)
```

## Melding lifecycle

`MeldingCreateAction` first saves the new melding, then calls the classifier with its text. It assigns the returned classification, stores the raw adapter result in `Melding.classifier_adapter_result_initial`, transitions the melding through `MeldingTransitions.CLASSIFY`, and saves it again.

`MeldingUpdateActionMelder` runs classification again for the updated melding text. It passes the old and new classifications to its `BaseReclassification` implementation so the application can update classification-dependent data, assigns the new classification, transitions the melding to the classified state, and saves it. This action does not store the adapter result from the reclassification. If a `ClassificationNotFoundException` escapes the classifier (for example, because the default classification cannot be found), this action logs the error and reclassifies with `None`; other errors propagate.

An authorized caller can also assign an existing classification directly through `MeldingUpdateAction` by providing its ID. This is a manual assignment, not a classifier run. It invokes the reclassification hook when the classification changes; the action refuses this path once the melding has reached a backoffice state.

## Classifier error codes

Adapter and lookup problems are logged and the classifier attempts to use the configured default:

| Code | Meaning |
| --- | --- |
| `CLASSIFIER_ADAPTER_FAILED` | An adapter raised an exception; the next adapter is tried. |
| `CLASSIFIER_ADAPTER_RETURNED_NONE` | An individual adapter returned `None`; the next adapter is tried. |
| `CLASSIFIER_CLASSIFICATION_NOT_FOUND` | An adapter returned a name that the classification repository could not find; the default is selected. |
| `CLASSIFIER_ADAPTERS_NO_RESULT` | No adapter produced a classification name: all returned `None` or failed, or no adapters were configured. The default classification is selected. |

These are log codes, not exceptions returned for ordinary adapter failures. Errors from looking up the configured default are not swallowed.

## Classifier adapters

Implement `BaseClassifierAdapter` and its asynchronous `__call__(text)` method. Set the adapter's `name` in its constructor; it is included in error logs. Adapters only return a classification name—the classifier resolves that name to the application's `Classification` object. Keep the list order intentional because the first adapter returning a non-`None` result wins.
