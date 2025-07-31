import graphene
from fhir.resources import FHIRAbstractModel


class FHIRResourceGQLType(graphene.ObjectType):
    """
    Base GraphQL type for FHIR resources
    """

    resourceType = graphene.String(description="The type of FHIR resource")
    id = graphene.String(description="Logical id of this artifact")
    meta = graphene.JSONString(description="Metadata about the resource")
    implicitRules = graphene.String(
        description="A set of rules under which this content was created"
    )
    language = graphene.String(description="Language of the resource content")
    text = graphene.JSONString(description="Text summary of the resource")
    contained = graphene.List(
        graphene.JSONString, description="Contained, inline Resources"
    )
    extension = graphene.List(
        graphene.JSONString, description="Additional content defined by implementations"
    )
    modifierExtension = graphene.List(
        graphene.JSONString, description="Extensions that cannot be ignored"
    )

    @classmethod
    def from_fhir(cls, fhir_resource, resource_type):
        """
        Convert FHIR resource to GraphQL type
        """
        if not fhir_resource:
            return None

        return cls(
            resourceType=resource_type,
            id=fhir_resource.id,
            meta=fhir_resource.meta.model_dump() if fhir_resource.meta else None,
            implicitRules=fhir_resource.implicitRules,
            language=fhir_resource.language,
            text=fhir_resource.text.model_dump() if fhir_resource.text else None,
            contained=[resource.model_dump() for resource in fhir_resource.contained]
            if fhir_resource.contained
            else None,
            extension=[ext.model_dump() for ext in fhir_resource.extension]
            if fhir_resource.extension
            else None,
            modifierExtension=[
                ext.model_dump() for ext in fhir_resource.modifierExtension
            ]
            if fhir_resource.modifierExtension
            else None,
        )

    def to_fhir(self) -> FHIRAbstractModel:
        """
        Convert GraphQL type to FHIR resource
        This is a base implementation that should be overridden by specific resource types
        """
        raise NotImplementedError(
            "to_fhir() must be implemented by specific resource types"
        )


# Import all the separated types
from .identifier import IdentifierGQLType
from .coding import CodingGQLType
from .codeable_concept import CodeableConceptGQLType
from .reference import ReferenceGQLType
from .quantity import QuantityGQLType
from .money import MoneyGQLType
from .period import PeriodGQLType
from .human_name import HumanNameGQLType
from .contact_point import ContactPointGQLType
from .address import AddressGQLType

__all__ = [
    "FHIRResourceGQLType",
    "IdentifierGQLType",
    "CodingGQLType",
    "CodeableConceptGQLType",
    "ReferenceGQLType",
    "QuantityGQLType",
    "MoneyGQLType",
    "PeriodGQLType",
    "HumanNameGQLType",
    "ContactPointGQLType",
    "AddressGQLType",
]
