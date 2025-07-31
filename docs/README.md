# Developer Documentation

This document provides comprehensive guidance for developers working with the GraphQL FHIR Converter library.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Creating Converters](#creating-converters)
4. [Creating FHIR GraphQL Types](#creating-fhir-graphql-types)
5. [Best Practices](#best-practices)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Overview

The GraphQL FHIR Converter library provides a framework for converting between:
- Your application's data models (e.g., Django models)
- FHIR resources (standardized healthcare data)
- GraphQL types (for API responses)

### Key Concepts

- **Converters**: Transform your data models to/from FHIR resources
- **FHIR GraphQL Types**: GraphQL representations of FHIR resources
- **Base Classes**: Abstract interfaces that define the conversion contract

## Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Model    │───▶│    Converter     │───▶│  FHIR Resource  │
│  (e.g., Insuree)│    │  (PatientConverter)│    │   (Patient)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ FHIR GraphQL    │
                       │ Type (Patient)  │
                       └─────────────────┘
```

### File Structure

```
graphql_fhir_converter/
├── converters/
│   ├── __init__.py
│   ├── base.py              # Base converter interface
│   └── patient.py           # Patient-specific converter
├── fhir_gql_types/
│   ├── __init__.py
│   ├── base.py              # Base GraphQL type
│   ├── patient.py           # Patient GraphQL type
│   ├── identifier.py        # Identifier GraphQL type
│   └── ...                  # Other FHIR types
```

## Creating Converters

### Step 1: Understand the Base Interface

All converters must implement the `BaseFHIRToGraphQLConverter` interface:

```python
from abc import ABC, abstractmethod

class BaseFHIRToGraphQLConverter(ABC):
    @classmethod
    @abstractmethod
    def build_fhir_obj(cls, data_obj):
        """Convert your data model to FHIR resource"""
        pass

    @classmethod
    @abstractmethod
    def convert_to_gql_fhir(cls, data_obj):
        """Convert your data model to GraphQL type"""
        pass
```

### Step 2: Create Your Converter

Here's a complete example for creating an Observation converter:

```python
from graphql_fhir_converter.converters.base import BaseFHIRToGraphQLConverter
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from ..fhir_gql_types.observation import ObservationGQLType

class ObservationConverter(BaseFHIRToGraphQLConverter):
    """
    Converter for Observation FHIR resource
    """
    
    @classmethod
    def build_fhir_obj(cls, data_obj):
        """
        Convert your data model to FHIR Observation
        
        Args:
            data_obj: Your application's data model (e.g., LabResult)
            
        Returns:
            Observation: FHIR Observation resource
        """
        observation = Observation.model_construct()
        
        # Set basic resource properties
        observation.id = str(data_obj.uuid) if data_obj.uuid else str(data_obj.id)
        observation.status = cls._map_status(data_obj.status)
        
        # Set subject (patient reference)
        if data_obj.patient:
            subject_ref = Reference.model_construct()
            subject_ref.reference = f"Patient/{data_obj.patient.uuid}"
            observation.subject = subject_ref
        
        # Set code (what was observed)
        if data_obj.test_type:
            code = CodeableConcept.model_construct()
            coding = Coding.model_construct()
            coding.system = "http://loinc.org"
            coding.code = data_obj.test_type.code
            coding.display = data_obj.test_type.name
            code.coding = [coding]
            observation.code = code
        
        # Set value
        if data_obj.result_value:
            observation.valueQuantity = cls._create_quantity(
                data_obj.result_value, 
                data_obj.unit
            )
        
        # Set effective time
        if data_obj.test_date:
            observation.effectiveDateTime = data_obj.test_date
        
        # Set issued time
        if data_obj.created_at:
            observation.issued = data_obj.created_at
        
        return observation
    
    @classmethod
    def convert_to_gql_fhir(cls, data_obj):
        """
        Convert your data model to GraphQL Observation type
        
        Args:
            data_obj: Your application's data model
            
        Returns:
            ObservationGQLType: GraphQL Observation type
        """
        fhir_observation = cls.build_fhir_obj(data_obj)
        return ObservationGQLType.from_fhir(fhir_observation)
    
    @classmethod
    def _map_status(cls, status):
        """Map your status to FHIR status values"""
        status_mapping = {
            'pending': 'registered',
            'in_progress': 'preliminary',
            'completed': 'final',
            'amended': 'amended',
            'cancelled': 'cancelled'
        }
        return status_mapping.get(status, 'unknown')
    
    @classmethod
    def _create_quantity(cls, value, unit):
        """Create FHIR Quantity from value and unit"""
        from fhir.resources.quantity import Quantity
        
        quantity = Quantity.model_construct()
        quantity.value = float(value)
        quantity.unit = unit
        quantity.system = "http://unitsofmeasure.org"
        quantity.code = cls._map_unit_code(unit)
        
        return quantity
    
    @classmethod
    def _map_unit_code(cls, unit):
        """Map unit to standard UCUM codes"""
        unit_mapping = {
            'mg/dL': 'mg/dL',
            'mmol/L': 'mmol/L',
            'g/dL': 'g/dL',
            'cells/μL': '10*3/uL'
        }
        return unit_mapping.get(unit, unit)
```

### Step 3: Handle Complex Relationships

For complex relationships, use nested converters:

```python
class EncounterConverter(BaseFHIRToGraphQLConverter):
    @classmethod
    def build_fhir_obj(cls, data_obj):
        encounter = Encounter.model_construct()
        
        # Basic properties
        encounter.id = str(data_obj.uuid)
        encounter.status = cls._map_encounter_status(data_obj.status)
        
        # Patient reference
        if data_obj.patient:
            patient_ref = Reference.model_construct()
            patient_ref.reference = f"Patient/{data_obj.patient.uuid}"
            encounter.subject = patient_ref
        
        # Service provider (organization)
        if data_obj.facility:
            org_ref = Reference.model_construct()
            org_ref.reference = f"Organization/{data_obj.facility.uuid}"
            encounter.serviceProvider = org_ref
        
        # Period
        if data_obj.start_date or data_obj.end_date:
            period = Period.model_construct()
            if data_obj.start_date:
                period.start = data_obj.start_date
            if data_obj.end_date:
                period.end = data_obj.end_date
            encounter.period = period
        
        # Extensions for custom fields
        extensions = []
        
        if data_obj.visit_type:
            visit_ext = Extension.model_construct()
            visit_ext.url = "http://your-org.org/StructureDefinition/encounter-visit-type"
            visit_ext.valueCodeableConcept = CodeableConcept.model_construct()
            visit_coding = Coding.model_construct()
            visit_coding.system = "http://your-org.org/CodeSystem/visit-type"
            visit_coding.code = data_obj.visit_type.code
            visit_coding.display = data_obj.visit_type.name
            visit_ext.valueCodeableConcept.coding = [visit_coding]
            extensions.append(visit_ext)
        
        encounter.extension = extensions
        
        return encounter
```

## Creating FHIR GraphQL Types

### Step 1: Understand the Base GraphQL Type

All FHIR GraphQL types extend `FHIRResourceGQLType`:

```python
import graphene
from fhir.resources import FHIRAbstractModel

class FHIRResourceGQLType(graphene.ObjectType):
    """Base GraphQL type for FHIR resources"""
    
    resourceType = graphene.String(description="The type of FHIR resource")
    id = graphene.String(description="Logical id of this artifact")
    meta = graphene.JSONString(description="Metadata about the resource")
    # ... other base fields
    
    @classmethod
    def from_fhir(cls, fhir_resource, resource_type):
        """Convert FHIR resource to GraphQL type"""
        # Implementation in base class
    
    def to_fhir(self) -> FHIRAbstractModel:
        """Convert GraphQL type to FHIR resource"""
        raise NotImplementedError("Must be implemented by specific types")
```

### Step 2: Create Your GraphQL Type

```python
import graphene
from .base import FHIRResourceGQLType
from .reference import ReferenceGQLType
from .codeable_concept import CodeableConceptGQLType
from .quantity import QuantityGQLType
from .period import PeriodGQLType

class ObservationGQLType(FHIRResourceGQLType):
    """GraphQL type for FHIR Observation"""
    
    # Basic fields
    status = graphene.String(description="registered | preliminary | final | amended +")
    category = graphene.List(CodeableConceptGQLType, description="Classification of type of observation")
    code = graphene.Field(CodeableConceptGQLType, description="Type of observation")
    
    # Subject and context
    subject = graphene.Field(ReferenceGQLType, description="Who and/or what the observation is about")
    encounter = graphene.Field(ReferenceGQLType, description="Healthcare event related to this observation")
    
    # Timing
    effectiveDateTime = graphene.String(description="Clinically relevant time/time-period for observation")
    effectivePeriod = graphene.Field(PeriodGQLType, description="Clinically relevant time/time-period for observation")
    issued = graphene.String(description="Date/Time this version was made available")
    
    # Values
    valueQuantity = graphene.Field(QuantityGQLType, description="Actual result")
    valueCodeableConcept = graphene.Field(CodeableConceptGQLType, description="Actual result")
    valueString = graphene.String(description="Actual result")
    valueBoolean = graphene.Boolean(description="Actual result")
    
    # Components (for multi-part observations)
    component = graphene.List('ObservationComponentGQLType', description="Component results")
    
    @classmethod
    def from_fhir(cls, fhir_observation):
        """Convert FHIR Observation to GraphQL type"""
        if not fhir_observation:
            return None
        
        # Get base FHIR resource fields
        base_fields = super().from_fhir(fhir_observation, "Observation")
        
        # Convert specific Observation fields
        category_list = []
        if fhir_observation.category:
            for cat in fhir_observation.category:
                cat_gql = CodeableConceptGQLType.from_fhir(cat)
                if cat_gql:
                    category_list.append(cat_gql)
        
        component_list = []
        if fhir_observation.component:
            for comp in fhir_observation.component:
                comp_gql = ObservationComponentGQLType.from_fhir(comp)
                if comp_gql:
                    component_list.append(comp_gql)
        
        return cls(
            # Base fields
            resourceType=base_fields.resourceType,
            id=base_fields.id,
            meta=base_fields.meta,
            extension=base_fields.extension,
            modifierExtension=base_fields.modifierExtension,
            
            # Observation specific fields
            status=fhir_observation.status,
            category=category_list,
            code=CodeableConceptGQLType.from_fhir(fhir_observation.code),
            subject=ReferenceGQLType.from_fhir(fhir_observation.subject),
            encounter=ReferenceGQLType.from_fhir(fhir_observation.encounter),
            effectiveDateTime=fhir_observation.effectiveDateTime.isoformat() 
                if fhir_observation.effectiveDateTime else None,
            effectivePeriod=PeriodGQLType.from_fhir(fhir_observation.effectivePeriod),
            issued=fhir_observation.issued.isoformat() 
                if fhir_observation.issued else None,
            valueQuantity=QuantityGQLType.from_fhir(fhir_observation.valueQuantity),
            valueCodeableConcept=CodeableConceptGQLType.from_fhir(fhir_observation.valueCodeableConcept),
            valueString=fhir_observation.valueString,
            valueBoolean=fhir_observation.valueBoolean,
            component=component_list,
        )
    
    def to_fhir(self) -> Observation:
        """Convert GraphQL type to FHIR Observation"""
        from fhir.resources.observation import Observation
        
        data = {
            "id": self.id,
            "status": self.status,
        }
        
        if self.code:
            data["code"] = self.code.to_fhir()
        
        if self.subject:
            data["subject"] = self.subject.to_fhir()
        
        if self.effectiveDateTime:
            from datetime import datetime
            data["effectiveDateTime"] = datetime.fromisoformat(self.effectiveDateTime)
        
        if self.valueQuantity:
            data["valueQuantity"] = self.valueQuantity.to_fhir()
        
        return Observation(**data)


class ObservationComponentGQLType(graphene.ObjectType):
    """GraphQL type for FHIR Observation Component"""
    
    code = graphene.Field(CodeableConceptGQLType, description="Type of component observation")
    valueQuantity = graphene.Field(QuantityGQLType, description="Actual component result")
    valueCodeableConcept = graphene.Field(CodeableConceptGQLType, description="Actual component result")
    valueString = graphene.String(description="Actual component result")
    valueBoolean = graphene.Boolean(description="Actual component result")
    
    @classmethod
    def from_fhir(cls, fhir_component):
        """Convert FHIR Observation Component to GraphQL type"""
        if not fhir_component:
            return None
        
        return cls(
            code=CodeableConceptGQLType.from_fhir(fhir_component.code),
            valueQuantity=QuantityGQLType.from_fhir(fhir_component.valueQuantity),
            valueCodeableConcept=CodeableConceptGQLType.from_fhir(fhir_component.valueCodeableConcept),
            valueString=fhir_component.valueString,
            valueBoolean=fhir_component.valueBoolean,
        )
```

### Step 3: Handle Complex Types

For complex FHIR types, create separate GraphQL types:

```python
class MedicationRequestGQLType(FHIRResourceGQLType):
    """GraphQL type for FHIR MedicationRequest"""
    
    # Basic fields
    status = graphene.String(description="active | on-hold | cancelled | completed | ...")
    intent = graphene.String(description="proposal | plan | order | original-order | ...")
    
    # References
    medicationCodeableConcept = graphene.Field(CodeableConceptGQLType, description="Medication to be taken")
    medicationReference = graphene.Field(ReferenceGQLType, description="Medication to be taken")
    subject = graphene.Field(ReferenceGQLType, description="Who the medication is for")
    requester = graphene.Field(ReferenceGQLType, description="Who/What requested the Request")
    
    # Dosage
    dosageInstruction = graphene.List('DosageGQLType', description="How the medication should be taken")
    
    @classmethod
    def from_fhir(cls, fhir_med_request):
        """Convert FHIR MedicationRequest to GraphQL type"""
        if not fhir_med_request:
            return None
        
        base_fields = super().from_fhir(fhir_med_request, "MedicationRequest")
        
        dosage_list = []
        if fhir_med_request.dosageInstruction:
            for dosage in fhir_med_request.dosageInstruction:
                dosage_gql = DosageGQLType.from_fhir(dosage)
                if dosage_gql:
                    dosage_list.append(dosage_gql)
        
        return cls(
            # Base fields
            resourceType=base_fields.resourceType,
            id=base_fields.id,
            
            # MedicationRequest specific fields
            status=fhir_med_request.status,
            intent=fhir_med_request.intent,
            medicationCodeableConcept=CodeableConceptGQLType.from_fhir(
                fhir_med_request.medicationCodeableConcept
            ),
            medicationReference=ReferenceGQLType.from_fhir(
                fhir_med_request.medicationReference
            ),
            subject=ReferenceGQLType.from_fhir(fhir_med_request.subject),
            requester=ReferenceGQLType.from_fhir(fhir_med_request.requester),
            dosageInstruction=dosage_list,
        )


class DosageGQLType(graphene.ObjectType):
    """GraphQL type for FHIR Dosage"""
    
    text = graphene.String(description="Free text dosage instructions")
    timing = graphene.JSONString(description="When medication should be administered")
    route = graphene.Field(CodeableConceptGQLType, description="How drug should enter body")
    method = graphene.Field(CodeableConceptGQLType, description="Technique for administering medication")
    doseAndRate = graphene.List('DoseAndRateGQLType', description="Amount of medication administered")
    
    @classmethod
    def from_fhir(cls, fhir_dosage):
        """Convert FHIR Dosage to GraphQL type"""
        if not fhir_dosage:
            return None
        
        dose_and_rate_list = []
        if fhir_dosage.doseAndRate:
            for dar in fhir_dosage.doseAndRate:
                dar_gql = DoseAndRateGQLType.from_fhir(dar)
                if dar_gql:
                    dose_and_rate_list.append(dar_gql)
        
        return cls(
            text=fhir_dosage.text,
            timing=fhir_dosage.timing.model_dump() if fhir_dosage.timing else None,
            route=CodeableConceptGQLType.from_fhir(fhir_dosage.route),
            method=CodeableConceptGQLType.from_fhir(fhir_dosage.method),
            doseAndRate=dose_and_rate_list,
        )
```

## Best Practices

### 1. Error Handling

Always handle missing or invalid data gracefully:

```python
@classmethod
def build_fhir_obj(cls, data_obj):
    if not data_obj:
        return None
    
    try:
        observation = Observation.model_construct()
        observation.id = str(data_obj.id)
        # ... rest of conversion
        return observation
    except Exception as e:
        logger.error(f"Error converting {data_obj} to FHIR: {e}")
        return None
```

### 2. Validation

Validate FHIR resources after creation:

```python
from fhir.resources import construct_fhir_element

@classmethod
def build_fhir_obj(cls, data_obj):
    observation = Observation.model_construct()
    # ... set properties
    
    # Validate the FHIR resource
    try:
        validated_observation = construct_fhir_element("Observation", observation.model_dump())
        return validated_observation
    except Exception as e:
        logger.error(f"FHIR validation failed: {e}")
        return observation  # Return unvalidated or handle error
```

### 3. Performance Optimization

For large datasets, consider lazy loading:

```python
class PatientConverter(BaseFHIRToGraphQLConverter):
    @classmethod
    def build_fhir_obj(cls, data_obj):
        patient = Patient.model_construct()
        
        # Only load related objects when needed
        if hasattr(data_obj, '_prefetched_related_objects'):
            # Use prefetched data
            pass
        else:
            # Load data as needed
            pass
        
        return patient
```

### 4. Extensions

Use FHIR extensions for custom fields:

```python
def _build_extensions(cls, data_obj):
    """Build OpenIMIS-specific extensions"""
    extensions = []
    
    # Education level extension
    if hasattr(data_obj, 'education') and data_obj.education:
        education_ext = Extension.model_construct()
        education_ext.url = "http://openimis.org/StructureDefinition/patient-education-level"
        education_ext.valueCodeableConcept = CodeableConcept.model_construct()
        education_coding = Coding.model_construct()
        education_coding.system = "http://openimis.org/CodeSystem/patient-education-level"
        education_coding.code = str(data_obj.education.id)
        education_coding.display = str(data_obj.education.education)
        education_ext.valueCodeableConcept.coding = [education_coding]
        extensions.append(education_ext)
    
    return extensions
```

## Testing

### 1. Unit Tests for Converters

```python
import pytest
from unittest.mock import Mock
from graphql_fhir_converter.converters.patient import PatientConverter

class TestPatientConverter:
    def test_build_fhir_obj_basic(self):
        # Create mock data object
        mock_insuree = Mock()
        mock_insuree.id = 1
        mock_insuree.uuid = "test-uuid"
        mock_insuree.chf_id = "CHF123456"
        mock_insuree.last_name = "Doe"
        mock_insuree.other_names = "John"
        mock_insuree.status = "A"
        
        # Convert to FHIR
        fhir_patient = PatientConverter.build_fhir_obj(mock_insuree)
        
        # Assertions
        assert fhir_patient.id == "test-uuid"
        assert fhir_patient.active is True
        assert len(fhir_patient.identifier) == 1
        assert fhir_patient.identifier[0].value == "CHF123456"
        assert len(fhir_patient.name) == 1
        assert fhir_patient.name[0].family == "Doe"
        assert fhir_patient.name[0].given == ["John"]
    
    def test_convert_to_gql_fhir(self):
        mock_insuree = Mock()
        # ... setup mock data
        
        gql_patient = PatientConverter.convert_to_gql_fhir(mock_insuree)
        
        assert gql_patient.id == "test-uuid"
        assert gql_patient.active is True
        # ... more assertions
```

### 2. Integration Tests

```python
import pytest
from django.test import TestCase
from insuree.models import Insuree
from graphql_fhir_converter.converters.patient import PatientConverter

class TestPatientConverterIntegration(TestCase):
    def setUp(self):
        # Create test data
        self.insuree = Insuree.objects.create(
            chf_id="CHF123456",
            last_name="Doe",
            other_names="John",
            status="A"
        )
    
    def test_full_conversion_pipeline(self):
        # Convert to FHIR
        fhir_patient = PatientConverter.build_fhir_obj(self.insuree)
        
        # Convert to GraphQL
        gql_patient = PatientConverter.convert_to_gql_fhir(self.insuree)
        
        # Verify both conversions work
        assert fhir_patient.id == str(self.insuree.uuid)
        assert gql_patient.id == str(self.insuree.uuid)
        assert gql_patient.active == fhir_patient.active
```

### 3. GraphQL Schema Tests

```python
import pytest
from graphene.test import Client
from your_app.schema import schema

class TestGraphQLSchema:
    def test_patient_query(self):
        client = Client(schema)
        
        query = '''
        query GetPatient($id: String!) {
            patient(id: $id) {
                id
                active
                name {
                    family
                    given
                }
                identifier {
                    value
                    system
                }
            }
        }
        '''
        
        result = client.execute(query, variable_values={'id': 'test-uuid'})
        
        assert 'errors' not in result
        assert result['data']['patient']['id'] == 'test-uuid'
```

## Troubleshooting

### Common Issues

1. **FHIR Validation Errors**
   - Ensure all required fields are set
   - Check data types match FHIR specifications
   - Use FHIR validation tools

2. **GraphQL Type Errors**
   - Verify all fields are properly defined
   - Check for circular imports
   - Ensure `from_fhir` method handles None values

3. **Performance Issues**
   - Use database prefetching for related objects
   - Implement caching for frequently accessed data
   - Consider pagination for large datasets

### Debugging Tips

1. **Enable Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

2. **Validate FHIR Resources**
```python
from fhir.resources import construct_fhir_element

def validate_fhir_resource(resource_type, data):
    try:
        validated = construct_fhir_element(resource_type, data)
        return True
    except Exception as e:
        logger.error(f"FHIR validation failed: {e}")
        return False
```

3. **Test Individual Components**
```python
# Test just the FHIR conversion
fhir_obj = YourConverter.build_fhir_obj(data_obj)
print(fhir_obj.model_dump())

# Test just the GraphQL conversion
gql_obj = YourGQLType.from_fhir(fhir_obj)
print(gql_obj.__dict__)
```

## Additional Resources

- [FHIR Specification](https://www.hl7.org/fhir/)
- [GraphQL Documentation](https://graphql.org/)
- [OpenIMIS Documentation](https://openimis.github.io/)
- [Django Documentation](https://docs.djangoproject.com/) 