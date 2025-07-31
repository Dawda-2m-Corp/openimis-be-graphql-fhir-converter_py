from .base import BaseFHIRToGraphQLConverter
from ..fhir_gql_types.patient import PatientGQLType
from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.extension import Extension
from fhir.resources.attachment import Attachment
from datetime import datetime
from django.utils import timezone


class PatientConverter(BaseFHIRToGraphQLConverter):
    """
    Converter for Patient GQL type
    """

    @classmethod
    def build_fhir_obj(cls, data_obj):
        """
        Build FHIR Patient object from Insuree model
        """
        patient = Patient.model_construct()

        # Set basic resource properties
        patient.id = str(data_obj.uuid) if data_obj.uuid else str(data_obj.id)

        # Set active status based on insuree status
        patient.active = data_obj.status == "A" if hasattr(data_obj, "status") else True

        # Build identifiers
        identifiers = []

        # CHF ID identifier
        if data_obj.chf_id:
            chf_identifier = Identifier.model_construct()
            chf_identifier.use = "official"
            chf_identifier.system = "http://openimis.org/identifiers/chf"
            chf_identifier.value = data_obj.chf_id
            identifiers.append(chf_identifier)

        # Passport identifier
        if data_obj.passport:
            passport_identifier = Identifier.model_construct()
            passport_identifier.use = "secondary"
            passport_identifier.system = "http://openimis.org/identifiers/passport"
            passport_identifier.value = data_obj.passport
            identifiers.append(passport_identifier)

        patient.identifier = identifiers

        # Build human names
        names = []
        if data_obj.last_name or data_obj.other_names:
            name = HumanName.model_construct()
            name.use = "official"
            name.family = data_obj.last_name or ""
            name.given = [data_obj.other_names] if data_obj.other_names else []
            names.append(name)

        patient.name = names

        # Build telecom (contact points)
        telecom = []

        # Phone
        if data_obj.phone:
            phone_contact = ContactPoint.model_construct()
            phone_contact.system = "phone"
            phone_contact.value = data_obj.phone
            phone_contact.use = "home"
            telecom.append(phone_contact)

        # Email
        if data_obj.email:
            email_contact = ContactPoint.model_construct()
            email_contact.system = "email"
            email_contact.value = data_obj.email
            email_contact.use = "home"
            telecom.append(email_contact)

        patient.telecom = telecom

        # Set gender
        if data_obj.gender:
            gender_mapping = {"M": "male", "F": "female", "O": "other"}
            patient.gender = gender_mapping.get(data_obj.gender.code, "unknown")

        # Set birth date
        if data_obj.dob:
            if isinstance(data_obj.dob, datetime):
                patient.birthDate = data_obj.dob.date().isoformat()
            else:
                patient.birthDate = data_obj.dob.isoformat()

        # Build addresses
        addresses = []
        if data_obj.current_address or data_obj.current_village:
            address = Address.model_construct()
            address.use = "home"
            address.type = "physical"

            if data_obj.current_address:
                address.text = data_obj.current_address

            # Add location reference extension if current_village exists
            if data_obj.current_village:
                location_ext = Extension.model_construct()
                location_ext.url = (
                    "http://openimis.org/StructureDefinition/address-location-reference"
                )
                location_ext.valueReference = Reference.model_construct()
                location_ext.valueReference.reference = (
                    f"Location/{data_obj.current_village.uuid}"
                )
                address.extension = [location_ext]

            addresses.append(address)

        patient.address = addresses

        # Set marital status
        if data_obj.marital:
            marital_status = CodeableConcept.model_construct()
            marital_coding = Coding.model_construct()
            marital_coding.system = "http://openimis.org/CodeSystem/marital-status"
            marital_coding.code = data_obj.marital
            marital_status.coding = [marital_coding]
            patient.maritalStatus = marital_status

        # Build extensions for additional IMIS-specific data
        extensions = []

        # Head of family extension
        if hasattr(data_obj, "head") and data_obj.head is not None:
            head_ext = Extension.model_construct()
            head_ext.url = "http://openimis.org/StructureDefinition/patient-is-head"
            head_ext.valueBoolean = data_obj.head
            extensions.append(head_ext)

        # Education level extension
        if hasattr(data_obj, "education") and data_obj.education:
            education_ext = Extension.model_construct()
            education_ext.url = (
                "http://openimis.org/StructureDefinition/patient-education-level"
            )
            education_ext.valueCodeableConcept = CodeableConcept.model_construct()
            education_coding = Coding.model_construct()
            education_coding.system = (
                "http://openimis.org/CodeSystem/patient-education-level"
            )
            education_coding.code = str(data_obj.education.id)
            education_coding.display = str(data_obj.education.education)
            education_ext.valueCodeableConcept.coding = [education_coding]
            extensions.append(education_ext)

        # Profession extension
        if hasattr(data_obj, "profession") and data_obj.profession:
            profession_ext = Extension.model_construct()
            profession_ext.url = (
                "http://openimis.org/StructureDefinition/patient-profession"
            )
            profession_ext.valueCodeableConcept = CodeableConcept.model_construct()
            profession_coding = Coding.model_construct()
            profession_coding.system = (
                "http://openimis.org/CodeSystem/patient-profession"
            )
            profession_coding.code = str(data_obj.profession.id)
            profession_coding.display = str(data_obj.profession.profession)
            profession_ext.valueCodeableConcept.coding = [profession_coding]
            extensions.append(profession_ext)

        # Card issued extension
        if hasattr(data_obj, "card_issued") and data_obj.card_issued is not None:
            card_ext = Extension.model_construct()
            card_ext.url = "http://openimis.org/StructureDefinition/patient-card-issued"
            card_ext.valueBoolean = data_obj.card_issued
            extensions.append(card_ext)

        # Family reference extension
        if hasattr(data_obj, "family") and data_obj.family:
            family_ext = Extension.model_construct()
            family_ext.url = (
                "http://openimis.org/StructureDefinition/patient-group-reference"
            )
            family_ext.valueReference = Reference.model_construct()
            family_ext.valueReference.reference = f"Group/{data_obj.family.uuid}"
            extensions.append(family_ext)

        # Identification extension
        if (
            hasattr(data_obj, "type_of_id")
            and data_obj.type_of_id
            and hasattr(data_obj, "passport")
            and data_obj.passport
        ):
            id_ext = Extension.model_construct()
            id_ext.url = (
                "http://openimis.org/StructureDefinition/patient-identification"
            )
            id_ext.extension = []

            # Number sub-extension
            number_sub_ext = Extension.model_construct()
            number_sub_ext.url = "number"
            number_sub_ext.valueString = data_obj.passport
            id_ext.extension.append(number_sub_ext)

            # Type sub-extension
            type_sub_ext = Extension.model_construct()
            type_sub_ext.url = "type"
            type_sub_ext.valueCodeableConcept = CodeableConcept.model_construct()
            type_coding = Coding.model_construct()
            type_coding.system = "http://openimis.org/CodeSystem/identification-type"
            type_coding.code = data_obj.type_of_id.code
            type_coding.display = data_obj.type_of_id.identification_type
            type_sub_ext.valueCodeableConcept.coding = [type_coding]
            id_ext.extension.append(type_sub_ext)

            extensions.append(id_ext)

        patient.extension = extensions

        # Build photo attachment
        if hasattr(data_obj, "photo") and data_obj.photo:
            photo = Attachment.model_construct()
            photo.contentType = "image/jpeg"  # Default to JPEG
            photo.title = f"Photo of {data_obj.last_name} {data_obj.other_names}"
            photo.creation = timezone.now()
            # Note: In a real implementation, you'd need to handle the actual photo data
            # This is a placeholder for the photo structure
            patient.photo = [photo]

        # Build general practitioner reference (health facility)
        if hasattr(data_obj, "health_facility") and data_obj.health_facility:
            gp_ref = Reference.model_construct()
            gp_ref.reference = f"Organization/{data_obj.health_facility.uuid}"
            patient.generalPractitioner = [gp_ref]

        # Build managing organization reference (secondary health facility)
        if (
            hasattr(data_obj, "secondary_health_facility")
            and data_obj.secondary_health_facility
        ):
            org_ref = Reference.model_construct()
            org_ref.reference = (
                f"Organization/{data_obj.secondary_health_facility.uuid}"
            )
            patient.managingOrganization = org_ref

        return patient

    @classmethod
    def convert_to_gql_fhir(cls, data_obj):
        fhir_patient = cls.build_fhir_obj(data_obj)
        patient_gql_type = PatientGQLType.from_fhir(fhir_patient)
        return patient_gql_type
