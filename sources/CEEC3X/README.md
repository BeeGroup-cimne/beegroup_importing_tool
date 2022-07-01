# GPG description
GPG(Gestió de Patrimoni de la Generalitat) is an application to manage the inventory of buildings and properties
belonging to the Generalitat de Catalunya. 

## Gathering tool
This data source comes in the format of an Excel file where each row is the information about a building. 

## Raw Data Format
The key of the file will be made using the unique field `Num_Ens_Inventari`, that will unequivocally identify each 
building. Future changes on the building will override the previous values. The rest of the file columns will be mapped
to the column family `info` with column using the raw format name.

| Source  |  class    | Hbase key          |
|---------|-----------|--------------------|
|  GPG    |  building | Num_Ens_Inventari  |

*Mapping key from GPG source*

## Import script information

For each import run a log document will be stored in mongo:
```json
{
    "user" : "the user that imported data",
    "logs": {
      "gather" : "list with the logs of the import",
      "logs.store" : "list with the logs of the store",
      "logs.harmonize" : "list with the logs of the harmonization"
    },
    "log_exec": "timestamp of execution"
}
```


## RUN import application
To run the import application, execute the python script with the following parameters:

```bash
python3 -m gather -so GPG -f <gpg file> -n <namespace> -u <user_importing> -st <storage>
```
###
"DatosDelCertificador" ==> NO
------
"IdentificacionEdificio" ==>
    Building->
        buildingName: "NombreDelEdificio"
        buildingConstructionYear: "AnoConstruccion"
        hasBuildingConstructionType ->
            BuildingConstructionType: taxonomy("TipoDeEdificio" :   {"ViviendaUnifamiliar", "BloqueDeViviendaCompleto", "ViviendaIndividualEnBloque", "EdificioUsoTerciario", "LocalUsoTerciario"})
    LocationInfo->
        addressStreetName: "Direccion"
        addressPostalCode: "CodigoPostal"
        hasAddressCity ->
            AddressCity: "Municipio" (fuzzy)
        hasAddressProvince ->
            AddressProvince -> "Provincia" (fuzzy)
        hasAddressClimateZone ->
            AddressClimateZone -> "ZonaClimatica" (fuzzy)
    CadastralInfo->
        landCadastralReference : "ReferenciaCatastral"
    EnergyPerformanceCertificate->
        energyPerformanceProcedureType : "Procedimiento"
        energyPerformanceCertificateClass : "AlcanceInformacionXML"
    EnergyPerformanceCertificateAdditionalInfo ->
        constructionRegulation : "NormativaVigente"
    NO->
        "ComunidadAutonoma"
------
"DatosGeneralesyGeometria" ==>
    BuildingSpace->
        hasArea->
            Area->
                value: "SuperficieHabitable"
                hasAreaType-> {NetFloorArea}
        hasArea->
            Area->
                value: "PorcentajeSuperficieHabitableCalefactada" * "SuperficieHabitable"
                hasAreaType-> {HeatedFloorArea}
        hasArea->
            Area->
                value: "PorcentajeSuperficieHabitableRefrigerada" * "SuperficieHabitable"
                hasAreaType-> {CooledFloorArea}
    NO->
        "DensidadFuentesInternas"
        "VentilacionUsoResidencial"
        "VentilacionTotal"
        "DemandaDiariaACS"
        "NumeroDePlantasSobreRasante"
        "NumeroDePlantasBajoRasante"
        "VolumenEspacioHabitable"
        "Compacidad"
        "PorcentajeSuperficieAcristalada"
        "Imagen"
        "Plano"
------
"DatosEnvolventeTermica"
    BuildingConstructionElement->
        For element in group_label:
            hasBuildingConstructionElementType -> taxonomy((group_label, Tipo) ,
                {CerramientosOpacos, HuecosyLucernarios, PuentesTermicos},
                {"Fachada", "Cubierta", "Suelo", "ParticionInteriorVertical","ParticionInteriorHorizontal","Adiabatico"})
            buildingConstructionElementIDFromOrganization: "Nombre"
            NO->
                "Superficie"
                "Orientacion"
                "Transmitancia"
                "FactorSolar"
                if group_label = HuecosyLurernarios:
                    ModoDeObtencionTransmitancia
                    ModoDeObtencionFactorSolar
                else =
                "ModoDeObtencion"
------
"InstalacionesTermicas"
    BuildingSystemElement->
        For element in group_label:
            hasBuildingSystemElementType -> taxonomy((group_label) ,
                {GeneradoresDeCalefaccion, GeneradoresDeRefrigeracion, InstalacionesACS, SistemasSecundariosCalefaccionRefrigeracion},
            buildingSystemElementIDFromOrganization: "Nombre"
            NO->
                "Tipo"
                "PotenciaNominal"
                "RendimientoNominal"
                "RendimientoEstacional"
                "VectorEnergetico"
                "ModoDeObtencion"
------
"InstalacionesIluminacion"
    BuildingSpace->
        For element in list:
            buildingSpaceName : "Nombre"
            buildingSpaceIDFromOrganization: "Nombre"
            NO->
                "PotenciaInstalada"
                "VEEI"
                "IluminanciaMedia"
                "ModoDeObtencion"
------
"CondicionesFuncionamientoyOcupacion"
    BuildingSpace->
        For element in list:
            buildingSpaceName : "Nombre"
            buildingSpaceIDFromOrganization: "Nombre"
            hasArea->
                Area->
                    value : Superficie
                    hasAreaType->{NetFloorArea}
            NO->
                "NivelDeAcondicionamiento"
                "PerfilDeUso"
------
FALTA:

"EnergiasRenovables"
------
"Demanda"
------
"Consumo"
------
"EmisionesCO2"
------
"Calificacion"
------
"MedidasDeMejora"
------
"PruebasComprobacionesInspecciones"
