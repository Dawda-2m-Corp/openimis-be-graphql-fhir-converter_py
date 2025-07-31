# Quick Start Guide

This guide will help you get started with the GraphQL FHIR Converter library in minutes.

## Installation

```bash
pip install graphql-fhir-converter
```

## Basic Usage

### 1. Convert Your Data Model to FHIR

```python
from graphql_fhir_converter.converters.patient import PatientConverter

# Your Django model (example)
class Insuree:
    def __init__(self):
        self.id = 1
        self.uuid = "patient-123"
        self.chf_id = "CHF123456"
        self.last_name = "Doe"
        self.other_names = "John"
        self.status = "A"  # Active
        self.gender = "M"
        self.dob = "1990-01-01"

# Create your data object
insuree = Insuree()

# Convert to FHIR Patient
fhir_patient = PatientConverter.build_fhir_obj(insuree)
print(f"FHIR Patient ID: {fhir_patient.id}")
print(f"Active: {fhir_patient.active}")
print(f"Name: {fhir_patient.name[0].family} {fhir_patient.name[0].given[0]}")
```

### 2. Convert to GraphQL Type

```python
# Convert to GraphQL type for API response
patient_gql = PatientConverter.convert_to_gql_fhir(insuree)
print(f"GraphQL Patient ID: {patient_gql.id}")
print(f"Active: {patient_gql.active}")
```

### 3. Use in GraphQL Schema

```python
import graphene
from graphql_fhir_converter.fhir_gql_types.patient import PatientGQLType

class Query(graphene.ObjectType):
    patient = graphene.Field(PatientGQLType, id=graphene.String(required=True))
    
    def resolve_patient(self, info, id):
        # Fetch your data model
        insuree = get_insuree_by_id(id)  # Your data fetching logic
        return PatientConverter.convert_to_gql_fhir(insuree)

# Create schema
schema = graphene.Schema(query=Query)

# Test query
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

result = schema.execute(query, variable_values={'id': 'patient-123'})
print(result.data)
```

## Creating Your First Converter

### Step 1: Create a Simple Converter

```python
from graphql_fhir_converter.converters.base import BaseFHIRToGraphQLConverter
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference

class SimpleObservationConverter(BaseFHIRToGraphQLConverter):
    """Simple converter for lab results"""
    
    @classmethod
    def build_fhir_obj(cls, data_obj):
        """Convert your lab result to FHIR Observation"""
        observation = Observation.model_construct()
        
        # Set basic properties
        observation.id = str(data_obj.id)
        observation.status = "final"  # Assuming completed lab result
        
        # Set subject (patient reference)
        if data_obj.patient_id:
            subject_ref = Reference.model_construct()
            subject_ref.reference = f"Patient/{data_obj.patient_id}"
            observation.subject = subject_ref
        
        # Set test name as code
        if data_obj.test_name:
            from fhir.resources.codeableconcept import CodeableConcept
            from fhir.resources.coding import Coding
            
            code = CodeableConcept.model_construct()
            coding = Coding.model_construct()
            coding.system = "http://loinc.org"
            coding.code = data_obj.test_code or "unknown"
            coding.display = data_obj.test_name
            code.coding = [coding]
            observation.code = code
        
        # Set result value
        if data_obj.result_value:
            from fhir.resources.quantity import Quantity
            quantity = Quantity.model_construct()
            quantity.value = float(data_obj.result_value)
            quantity.unit = data_obj.unit or "unknown"
            observation.valueQuantity = quantity
        
        return observation
    
    @classmethod
    def convert_to_gql_fhir(cls, data_obj):
        """Convert to GraphQL type"""
        # For now, return the FHIR object as JSON
        # You would create a proper GraphQL type later
        fhir_observation = cls.build_fhir_obj(data_obj)
        return fhir_observation.model_dump()
```

### Step 2: Test Your Converter

```python
# Test data
class LabResult:
    def __init__(self):
        self.id = 1
        self.patient_id = "patient-123"
        self.test_name = "Blood Glucose"
        self.test_code = "2339-0"
        self.result_value = "120"
        self.unit = "mg/dL"

# Test the converter
lab_result = LabResult()
fhir_observation = SimpleObservationConverter.build_fhir_obj(lab_result)

print(f"Observation ID: {fhir_observation.id}")
print(f"Status: {fhir_observation.status}")
print(f"Subject: {fhir_observation.subject.reference}")
print(f"Code: {fhir_observation.code.coding[0].display}")
print(f"Value: {fhir_observation.valueQuantity.value} {fhir_observation.valueQuantity.unit}")
```

## Creating Your First GraphQL Type

### Step 1: Create a Simple GraphQL Type

```python
import graphene
from graphql_fhir_converter.fhir_gql_types.base import FHIRResourceGQLType

class SimpleObservationGQLType(FHIRResourceGQLType):
    """Simple GraphQL type for Observation"""
    
    status = graphene.String(description="Observation status")
    subject = graphene.JSONString(description="Patient reference")
    code = graphene.JSONString(description="What was observed")
    valueQuantity = graphene.JSONString(description="Result value")
    
    @classmethod
    def from_fhir(cls, fhir_observation):
        """Convert FHIR Observation to GraphQL type"""
        if not fhir_observation:
            return None
        
        # Get base fields
        base_fields = super().from_fhir(fhir_observation, "Observation")
        
        return cls(
            # Base fields
            resourceType=base_fields.resourceType,
            id=base_fields.id,
            
            # Observation specific fields
            status=fhir_observation.status,
            subject=fhir_observation.subject.model_dump() if fhir_observation.subject else None,
            code=fhir_observation.code.model_dump() if fhir_observation.code else None,
            valueQuantity=fhir_observation.valueQuantity.model_dump() if fhir_observation.valueQuantity else None,
        )
```

### Step 2: Update Your Converter

```python
class SimpleObservationConverter(BaseFHIRToGraphQLConverter):
    # ... existing build_fhir_obj method ...
    
    @classmethod
    def convert_to_gql_fhir(cls, data_obj):
        """Convert to GraphQL type"""
        fhir_observation = cls.build_fhir_obj(data_obj)
        return SimpleObservationGQLType.from_fhir(fhir_observation)
```

### Step 3: Use in GraphQL Schema

```python
class Query(graphene.ObjectType):
    observation = graphene.Field(SimpleObservationGQLType, id=graphene.String(required=True))
    
    def resolve_observation(self, info, id):
        lab_result = get_lab_result_by_id(id)  # Your data fetching
        return SimpleObservationConverter.convert_to_gql_fhir(lab_result)

schema = graphene.Schema(query=Query)

# Test query
query = '''
query GetObservation($id: String!) {
    observation(id: $id) {
        id
        status
        code {
            coding {
                display
                code
            }
        }
        valueQuantity {
            value
            unit
        }
    }
}
'''

result = schema.execute(query, variable_values={'id': '1'})
print(result.data)
```

## OpenIMIS Integration Example

### Using with OpenIMIS Insuree Model

```python
from graphql_fhir_converter.converters.patient import PatientConverter
from insuree.models import Insuree  # OpenIMIS model

# Fetch OpenIMIS insuree
insuree = Insuree.objects.get(chf_id="CHF123456")

# Convert to FHIR Patient
fhir_patient = PatientConverter.build_fhir_obj(insuree)

# Convert to GraphQL for API
patient_gql = PatientConverter.convert_to_gql_fhir(insuree)

# Use in GraphQL query
query = '''
query GetPatient($chfId: String!) {
    patient(chfId: $chfId) {
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
        telecom {
            system
            value
        }
        address {
            text
        }
    }
}
'''
```

## Common Patterns

### 1. Handle Optional Fields

```python
@classmethod
def build_fhir_obj(cls, data_obj):
    observation = Observation.model_construct()
    
    # Always set required fields
    observation.id = str(data_obj.id)
    observation.status = "final"
    
    # Handle optional fields safely
    if hasattr(data_obj, 'patient_id') and data_obj.patient_id:
        subject_ref = Reference.model_construct()
        subject_ref.reference = f"Patient/{data_obj.patient_id}"
        observation.subject = subject_ref
    
    if hasattr(data_obj, 'result_value') and data_obj.result_value:
        quantity = Quantity.model_construct()
        quantity.value = float(data_obj.result_value)
        observation.valueQuantity = quantity
    
    return observation
```

### 2. Handle Date Fields

```python
from datetime import datetime

@classmethod
def build_fhir_obj(cls, data_obj):
    observation = Observation.model_construct()
    
    # Handle different date formats
    if data_obj.test_date:
        if isinstance(data_obj.test_date, str):
            observation.effectiveDateTime = data_obj.test_date
        elif isinstance(data_obj.test_date, datetime):
            observation.effectiveDateTime = data_obj.test_date.isoformat()
        else:
            observation.effectiveDateTime = str(data_obj.test_date)
    
    return observation
```

### 3. Handle Enumerations

```python
@classmethod
def _map_status(cls, status):
    """Map your status to FHIR status values"""
    status_mapping = {
        'pending': 'registered',
        'in_progress': 'preliminary', 
        'completed': 'final',
        'cancelled': 'cancelled'
    }
    return status_mapping.get(status, 'unknown')
```

## Next Steps

1. **Read the full documentation**: See `docs/README.md` for comprehensive guides
2. **Explore existing converters**: Study `converters/patient.py` for patterns
3. **Create your own converters**: Follow the patterns in this guide
4. **Add tests**: Use the testing examples in the documentation
5. **Contribute**: Submit pull requests for improvements

## Getting Help

- **Documentation**: `docs/README.md`
- **Issues**: GitHub Issues page
- **Email**: info@2m-corp.com
- **Examples**: Check the test files for usage examples 