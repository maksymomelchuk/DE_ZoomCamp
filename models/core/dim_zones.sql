{{ config(materialized='view') }}

select 
    locationid, 
    borough, 
    zone, 
    replace(service_zone,'Boro','Green') as service_zone

from {{ source('staging', 'zones')}}