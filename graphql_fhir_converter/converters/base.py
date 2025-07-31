from abc import ABC, abstractmethod


class BaseFHIRToGraphQLConverter(ABC):
    """
    Base class for FHIR to GraphQL converters
    """

    @classmethod
    @abstractmethod
    def build_fhir_obj(cls, data_obj):
        return NotImplementedError("build_fhir_obj is not implemented")

    @classmethod
    @abstractmethod
    def convert_to_gql_fhir(cls, data_obj):
        return NotImplementedError("convert_to_gql_fhir is not implemented")
