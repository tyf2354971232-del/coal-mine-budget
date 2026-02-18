"""Shared schema types."""
from datetime import datetime
from typing import Annotated, Optional
from pydantic.functional_serializers import PlainSerializer

FormattedDatetime = Annotated[
    datetime,
    PlainSerializer(lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None, return_type=str)
]

OptionalFormattedDatetime = Annotated[
    Optional[datetime],
    PlainSerializer(lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None, return_type=Optional[str])
]
