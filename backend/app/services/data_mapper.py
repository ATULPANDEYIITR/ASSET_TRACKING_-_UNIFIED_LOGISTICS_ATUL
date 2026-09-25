def map_record(
    record,
    mapping=None,
):
    mapping = mapping or {}

    result = {}

    for target, source in mapping.items():
        if source in record:
            result[target] = record[source]

    if "asset_code" in result:
        result["asset_code"] = str(
            result["asset_code"]
        )

    if "name" in result:
        result["name"] = str(
            result["name"]
        )

    if "description" in result:
        result["description"] = str(
            result["description"]
        )

    return result


def map_records(
    records,
    mapping=None,
):
    result = []

    for record in records:
        if isinstance(record, dict):
            mapped = map_record(
                record,
                mapping,
            )

            if mapped.get(
                "asset_code"
            ):
                result.append(mapped)

    return result
