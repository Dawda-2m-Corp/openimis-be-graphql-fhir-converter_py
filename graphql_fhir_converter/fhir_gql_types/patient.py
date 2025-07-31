import graphene
from fhir.resources.patient import Patient
from .base import FHIRResourceGQLType
from .identifier import IdentifierGQLType
from .human_name import HumanNameGQLType
from .contact_point import ContactPointGQLType
from .address import AddressGQLType
from .codeable_concept import CodeableConceptGQLType
from .reference import ReferenceGQLType
from .period import PeriodGQLType


class PatientContactGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Patient Contact
    """

    relationship = graphene.List(
        CodeableConceptGQLType, description="The kind of relationship"
    )
    name = graphene.Field(
        HumanNameGQLType, description="A name associated with the contact person"
    )
    telecom = graphene.List(
        ContactPointGQLType, description="A contact detail for the person"
    )
    address = graphene.Field(
        AddressGQLType, description="Address for the contact person"
    )
    gender = graphene.String(description="male | female | other | unknown")
    organization = graphene.Field(
        ReferenceGQLType, description="Organization that is associated with the contact"
    )
    period = graphene.Field(
        PeriodGQLType,
        description="The period during which this contact person or organization is valid",
    )

    @classmethod
    def from_fhir(cls, fhir_contact):
        """
        Convert FHIR Patient Contact to GraphQL type
        """
        if not fhir_contact:
            return None

        return cls(
            relationship=[
                CodeableConceptGQLType.from_fhir(rel)
                for rel in fhir_contact.get("relationship")
            ]
            if fhir_contact.get("relationship")
            else None,
            name=HumanNameGQLType.from_fhir(fhir_contact.name)
            if fhir_contact.name
            else None,
            telecom=[
                ContactPointGQLType.from_fhir(tel)
                for tel in fhir_contact.get("telecom")
            ]
            if fhir_contact.get("telecom")
            else None,
            address=AddressGQLType.from_fhir(fhir_contact.get("address"))
            if fhir_contact.get("address")
            else None,
            gender=fhir_contact.get("gender"),
            organization=ReferenceGQLType.from_fhir(fhir_contact.get("organization"))
            if fhir_contact.get("organization")
            else None,
            period=PeriodGQLType.from_fhir(fhir_contact.get("period"))
            if fhir_contact.get("period")
            else None,
        )


class PatientCommunicationGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Patient Communication
    """

    language = graphene.Field(
        CodeableConceptGQLType,
        description="The language which can be used to communicate with the patient",
    )
    preferred = graphene.Boolean(description="Language preference indicator")

    @classmethod
    def from_fhir(cls, fhir_communication):
        """
        Convert FHIR Patient Communication to GraphQL type
        """
        if not fhir_communication:
            return None

        return cls(
            language=CodeableConceptGQLType.from_fhir(
                fhir_communication.get("language")
            )
            if fhir_communication.get("language")
            else None,
            preferred=fhir_communication.get("preferred"),
        )


class PatientLinkGQLType(graphene.ObjectType):
    """
    GraphQL type for FHIR Patient Link
    """

    other = graphene.Field(
        ReferenceGQLType,
        description="The other patient or related person resource that the link refers to",
    )
    type = graphene.String(description="replaced-by | replaces | refer | seealso")

    @classmethod
    def from_fhir(cls, fhir_link):
        """
        Convert FHIR Patient Link to GraphQL type
        """
        if not fhir_link:
            return None

        return cls(
            other=ReferenceGQLType.from_fhir(fhir_link.get("other"))
            if fhir_link.get("other")
            else None,
            type=fhir_link.get("type"),
        )


class PatientGQLType(FHIRResourceGQLType):
    """
    GraphQL type for FHIR Patient resource
    """

    # Identifiers
    identifier = graphene.List(
        IdentifierGQLType, description="An identifier for this patient"
    )

    # Personal Information
    active = graphene.Boolean(
        description="Whether this patient's record is in active use"
    )
    name = graphene.List(
        HumanNameGQLType, description="A name associated with the individual"
    )
    telecom = graphene.List(
        ContactPointGQLType, description="A contact detail for the individual"
    )
    gender = graphene.String(description="male | female | other | unknown")
    birthDate = graphene.String(description="The date of birth for the individual")
    deceasedBoolean = graphene.Boolean(
        description="Indicates if the individual is deceased or not"
    )
    deceasedDateTime = graphene.String(
        description="Indicates the actual or approximate date of death"
    )

    # Address and Contact
    address = graphene.List(AddressGQLType, description="An address for the individual")
    maritalStatus = graphene.Field(
        CodeableConceptGQLType, description="Marital (civil) status of a patient"
    )
    multipleBirthBoolean = graphene.Boolean(
        description="Whether patient is part of a multiple birth"
    )
    multipleBirthInteger = graphene.Int(
        description="Whether patient is part of a multiple birth"
    )

    # Photo
    photo = graphene.List(graphene.JSONString, description="Image of the patient")

    # Contacts and Links
    contact = graphene.List(
        PatientContactGQLType,
        description="A contact party (e.g. guardian, partner, friend) for the patient",
    )
    communication = graphene.List(
        PatientCommunicationGQLType,
        description="A language which may be used to communicate with the patient",
    )

    # References
    generalPractitioner = graphene.List(
        ReferenceGQLType, description="Patient's nominated primary care provider"
    )
    managingOrganization = graphene.Field(
        ReferenceGQLType,
        description="Organization that is the custodian of the patient record",
    )
    link = graphene.List(
        PatientLinkGQLType,
        description="Link to another patient resource that concerns the same actual person",
    )

    @classmethod
    def from_fhir(cls, fhir_patient):
        """
        Convert FHIR Patient to GraphQL type
        """
        if not fhir_patient:
            return None

        # Get base FHIR resource fields
        base_fields = super().from_fhir(fhir_patient, "Patient")

        # Convert specific Patient fields
        identifier_list = []
        if fhir_patient.identifier:
            for ident in fhir_patient.identifier:
                ident_gql = IdentifierGQLType.from_fhir(ident)
                if ident_gql:
                    identifier_list.append(ident_gql)

        name_list = []
        if fhir_patient.name:
            for name in fhir_patient.name:
                name_gql = HumanNameGQLType.from_fhir(name)
                if name_gql:
                    name_list.append(name_gql)

        telecom_list = []
        if fhir_patient.telecom:
            for tel in fhir_patient.telecom:
                tel_gql = ContactPointGQLType.from_fhir(tel)
                if tel_gql:
                    telecom_list.append(tel_gql)

        address_list = []
        if fhir_patient.address:
            for addr in fhir_patient.address:
                addr_gql = AddressGQLType.from_fhir(addr)
                if addr_gql:
                    address_list.append(addr_gql)

        contact_list = []
        if fhir_patient.contact:
            for contact in fhir_patient.contact:
                contact_gql = PatientContactGQLType.from_fhir(contact)
                if contact_gql:
                    contact_list.append(contact_gql)

        communication_list = []
        if fhir_patient.communication:
            for comm in fhir_patient.communication:
                comm_gql = PatientCommunicationGQLType.from_fhir(comm)
                if comm_gql:
                    communication_list.append(comm_gql)

        general_practitioner_list = []
        if fhir_patient.generalPractitioner:
            for gp in fhir_patient.generalPractitioner:
                gp_gql = ReferenceGQLType.from_fhir(gp)
                if gp_gql:
                    general_practitioner_list.append(gp_gql)

        link_list = []
        if fhir_patient.link:
            for link in fhir_patient.link:
                link_gql = PatientLinkGQLType.from_fhir(link)
                if link_gql:
                    link_list.append(link_gql)

        return cls(
            # Base fields
            resourceType=base_fields.resourceType,
            id=base_fields.id,
            meta=base_fields.meta,
            implicitRules=base_fields.implicitRules,
            language=base_fields.language,
            text=base_fields.text,
            contained=base_fields.contained,
            extension=base_fields.extension,
            modifierExtension=base_fields.modifierExtension,
            # Patient specific fields
            identifier=identifier_list,
            active=fhir_patient.active,
            name=name_list,
            telecom=telecom_list,
            gender=fhir_patient.gender,
            birthDate=fhir_patient.birthDate.isoformat()
            if fhir_patient.birthDate
            else None,
            deceasedBoolean=fhir_patient.deceasedBoolean,
            deceasedDateTime=fhir_patient.deceasedDateTime.isoformat()
            if fhir_patient.deceasedDateTime
            else None,
            address=address_list,
            maritalStatus=CodeableConceptGQLType.from_fhir(fhir_patient.maritalStatus)
            if fhir_patient.maritalStatus
            else None,
            multipleBirthBoolean=fhir_patient.multipleBirthBoolean,
            multipleBirthInteger=fhir_patient.multipleBirthInteger,
            photo=[photo.model_dump() for photo in fhir_patient.photo]
            if fhir_patient.photo
            else None,
            contact=contact_list,
            communication=communication_list,
            generalPractitioner=general_practitioner_list,
            managingOrganization=ReferenceGQLType.from_fhir(
                fhir_patient.managingOrganization
            )
            if fhir_patient.managingOrganization
            else None,
            link=link_list,
        )

    def to_fhir(self) -> Patient:
        """
        Convert GraphQL type to FHIR Patient
        """
        # This would be implemented to convert back to FHIR Patient
        # For now, raise NotImplementedError
        raise NotImplementedError("to_fhir() for Patient is not yet implemented")
