__all__ = ["is_dataclass_instance", "dataclass_list_to_table"]

from dataclasses import fields, is_dataclass
from typing import Any

from prettytable import MARKDOWN, PrettyTable


def is_dataclass_instance(dataclass_instance: Any) -> bool:
    return is_dataclass(dataclass_instance) and not isinstance(dataclass_instance, type)


def dataclass_list_to_table(
    dataclass_list: list[Any], alignment: str | list[str] = "l"
) -> str:
    # The table header will come from the first item in the list. We'll also only do
    # a quick check to make sure this item is a dataclass instance.
    if len(dataclass_list) == 0:
        raise Exception("Invalid list size")
    if not is_dataclass_instance(dataclass_list[0]):
        raise TypeError("Unsupported data type")

    table_fields = fields(dataclass_list[0])
    table = PrettyTable()
    table.set_style(MARKDOWN)
    field_names = [field.name.replace("_", " ").title() for field in table_fields]
    table.field_names = field_names
    if isinstance(alignment, str):
        table.align = alignment
    else:
        table.align.update(dict(zip(field_names, alignment)))

    for dc in dataclass_list:
        values = [getattr(dc, x.name) for x in table_fields]
        table.add_row(values)

    return table.get_string()
