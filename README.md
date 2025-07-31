# GraphQL FHIR Converter

A Python library for converting between FHIR (Fast Healthcare Interoperability Resources) and GraphQL types. This library provides a robust framework for building healthcare applications that need to bridge the gap between FHIR standards and GraphQL APIs for **OpenIMIS**.

## Features

- **FHIR to GraphQL Conversion**: Convert FHIR resources to GraphQL types
- **GraphQL to FHIR Conversion**: Convert GraphQL types back to FHIR resources
- **Extensible Architecture**: Easy to extend for new FHIR resource types
- **Type Safety**: Full type hints and validation
- **Django Integration**: Built with Django compatibility in mind
- **OpenIMIS Support**: Specialized converters for OpenIMIS data models

### Development Installation

```bash
git clone https://github.com/2MCorp/openimis-be-graphql-fhir-converter_py
cd openimis-be-graphql-fhir-converter_py
pip install -e .
```

## Quick Start

### Basic Usage

```python
from graphql_fhir_converter.converters.patient import PatientConverter
from your_app.models import Insuree  # Your Django model

# Convert a Django model to FHIR Patient
insuree = Insuree.objects.get(id=1)
fhir_patient = PatientConverter.build_fhir_obj(insuree)

# Convert to GraphQL type
patient_gql = PatientConverter.convert_to_gql_fhir(insuree)
```

### Using in GraphQL Schema

```python
import graphene
from graphql_fhir_converter.fhir_gql_types.patient import PatientGQLType

class Query(graphene.ObjectType):
    patient = graphene.Field(PatientGQLType, id=graphene.String(required=True))

    def resolve_patient(self, info, id):
        # Fetch your data model
        insuree = Insuree.objects.get(id=id)
        # Convert to GraphQL type
        return PatientConverter.convert_to_gql_fhir(insuree)

schema = graphene.Schema(query=Query)
```

## Architecture

### Converters

Converters handle the transformation between your data models and FHIR resources. They implement the `BaseFHIRToGraphQLConverter` interface.

**Key Methods:**

- `build_fhir_obj()`: Converts your data model to FHIR resource
- `convert_to_gql_fhir()`: Converts your data model to GraphQL type

### FHIR GraphQL Types

GraphQL types that represent FHIR resources. They extend `FHIRResourceGQLType` and provide:

- **from_fhir()**: Convert FHIR resource to GraphQL type
- **to_fhir()**: Convert GraphQL type back to FHIR resource

## Creating Custom Converters

### 1. Create a New Converter

```python
from graphql_fhir_converter.converters.base import BaseFHIRToGraphQLConverter
from fhir.resources.observation import Observation
from ..fhir_gql_types.observation import ObservationGQLType

class ObservationConverter(BaseFHIRToGraphQLConverter):
    """Converter for Observation FHIR resource"""

    @classmethod
    def build_fhir_obj(cls, data_obj):
        """Convert your data model to FHIR Observation"""
        observation = Observation.model_construct()

        # Set basic properties
        observation.id = str(data_obj.id)
        observation.status = data_obj.status

        # Add more FHIR-specific mappings...

        return observation

    @classmethod
    def convert_to_gql_fhir(cls, data_obj):
        """Convert to GraphQL type"""
        fhir_observation = cls.build_fhir_obj(data_obj)
        return ObservationGQLType.from_fhir(fhir_observation)
```

### 2. Create Corresponding GraphQL Type

```python
import graphene
from .base import FHIRResourceGQLType

class ObservationGQLType(FHIRResourceGQLType):
    """GraphQL type for FHIR Observation"""

    status = graphene.String(description="registered | preliminary | final | amended +")
    code = graphene.JSONString(description="Type of observation")
    subject = graphene.JSONString(description="Who and/or what the observation is about")

    @classmethod
    def from_fhir(cls, fhir_observation):
        """Convert FHIR Observation to GraphQL type"""
        if not fhir_observation:
            return None

        base_fields = super().from_fhir(fhir_observation, "Observation")

        return cls(
            # Base fields
            resourceType=base_fields.resourceType,
            id=base_fields.id,
            # Observation specific fields
            status=fhir_observation.status,
            code=fhir_observation.code.model_dump() if fhir_observation.code else None,
            subject=fhir_observation.subject.model_dump() if fhir_observation.subject else None,
        )
```

## FHIR GraphQL Types Reference

### Base Types

- `FHIRResourceGQLType`: Base class for all FHIR resource GraphQL types
- `IdentifierGQLType`: FHIR Identifier
- `HumanNameGQLType`: FHIR HumanName
- `ContactPointGQLType`: FHIR ContactPoint
- `AddressGQLType`: FHIR Address
- `CodeableConceptGQLType`: FHIR CodeableConcept
- `CodingGQLType`: FHIR Coding
- `ReferenceGQLType`: FHIR Reference
- `QuantityGQLType`: FHIR Quantity
- `MoneyGQLType`: FHIR Money
- `PeriodGQLType`: FHIR Period

### Resource Types

- `PatientGQLType`: FHIR Patient resource
- `PatientContactGQLType`: FHIR Patient Contact
- `PatientCommunicationGQLType`: FHIR Patient Communication
- `PatientLinkGQLType`: FHIR Patient Link

## OpenIMIS Integration

This library includes specialized converters for OpenIMIS data models:

### Patient/Insuree Conversion

The `PatientConverter` handles conversion from OpenIMIS Insuree models to FHIR Patient resources, including:

- **Identifiers**: CHF ID, Passport numbers
- **Personal Information**: Names, contact details, demographics
- **Addresses**: Physical addresses with location references
- **Extensions**: OpenIMIS-specific extensions for education, profession, etc.

### Example OpenIMIS Usage

```python
from graphql_fhir_converter.converters.patient import PatientConverter
from insuree.models import Insuree

# Convert OpenIMIS Insuree to FHIR Patient
insuree = Insuree.objects.get(chf_id="CHF123456")
fhir_patient = PatientConverter.build_fhir_obj(insuree)

# Convert to GraphQL for API response
patient_gql = PatientConverter.convert_to_gql_fhir(insuree)
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=graphql_fhir_converter

# Run specific test file
pytest tests/test_patient_converter.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
flake8 graphql_fhir_converter

# Run type checking
mypy graphql_fhir_converter

# Format code
black graphql_fhir_converter
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Dawda Borje Kujabi** - _Initial work_ - [dawdaborjekujabi@gmail.com](mailto:dawdaborjekujabi@gmail.com)
- **2M Corp** - _Maintainer_ - [info@2m-corp.com](mailto:info@2m-corp.com)

## Acknowledgments

- FHIR community for the healthcare interoperability standards
- OpenIMIS community for the healthcare management system
- GraphQL community for the query language specification

## Support

For support and questions:

- Email: [info@2m-corp.com](mailto:info@2m-corp.com)
- Issues: [GitHub Issues](https://github.com/2m-corp/graphql-fhir-converter/issues)
- Documentation: [Read the Docs](https://graphql-fhir-converter.readthedocs.io/)
