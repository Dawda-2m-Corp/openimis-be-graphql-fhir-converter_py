import graphene
from fhir.resources.codeableconcept import CodeableConcept
from .coding import CodingGQLType


class CodeableConceptGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR CodeableConcept
    """

    coding = graphene.List(
        CodingGQLType, description="Code defined by a terminology system"
    )
    text = graphene.String(description="Plain text representation of the concept")

    @classmethod
    def from_fhir(cls, fhir_codeable_concept: CodeableConcept):
        """
        Convert FHIR CodeableConcept to GraphQL type
        """
        if not fhir_codeable_concept:
            return None

        # Convert coding list
        coding_list = []
        if fhir_codeable_concept.coding:
            for coding in fhir_codeable_concept.coding:
                coding_gql = CodingGQLType.from_fhir(coding)
                if coding_gql:
                    coding_list.append(coding_gql)

        return cls(coding=coding_list, text=fhir_codeable_concept.text)

    def to_fhir(self) -> CodeableConcept:
        """
        Convert GraphQL type to FHIR CodeableConcept
        """
        data = {"text": self.text}

        # Convert coding list
        if self.coding:
            coding_list = []
            for coding_gql in self.coding:
                coding_fhir = coding_gql.to_fhir()
                if coding_fhir:
                    coding_list.append(coding_fhir)
            data["coding"] = coding_list

        return CodeableConcept(**data)
