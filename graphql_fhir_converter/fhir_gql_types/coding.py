import graphene
from fhir.resources.coding import Coding


class CodingGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Coding
    """

    system = graphene.String(description="Identity of the terminology system")
    version = graphene.String(description="Version of the system - if relevant")
    code = graphene.String(description="Symbol in syntax defined by the system")
    display = graphene.String(description="Representation defined by the system")
    userSelected = graphene.Boolean(
        description="If this coding was chosen directly by the user"
    )

    @classmethod
    def from_fhir(cls, fhir_coding: Coding):
        """
        Convert FHIR Coding to GraphQL type
        """
        if not fhir_coding:
            return None

        return cls(
            system=fhir_coding.system,
            version=fhir_coding.version,
            code=fhir_coding.code,
            display=fhir_coding.display,
            userSelected=fhir_coding.userSelected,
        )

    def to_fhir(self) -> Coding:
        """
        Convert GraphQL type to FHIR Coding
        """
        data = {"system": self.system, "code": self.code, "display": self.display}

        if self.version:
            data["version"] = self.version
        if self.userSelected is not None:
            data["userSelected"] = self.userSelected

        return Coding(**data)
