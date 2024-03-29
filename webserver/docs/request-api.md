# CONTENT

**Note**: The Request Api is under development and may be updated in the future.

## Overview

Request Api is based web(python flask) formats. 


## Server struct

Nginx + gunicorn + flask

## Version

v2.0.0





---



## Opts - type

**Description**

Describe the operation types 

### Attributes

<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>address</strong></td>
  <td>string</td>
  <td>test .query address list for target chain(btc violas libra)</td>
 </tr>
 <tr>
  <td><strong>record</strong></td>
  <td>string</td>
  <td>abrogation. query records with address and operation type(swap/map).</td>
 </tr>
 <tr>
  <td><strong>records</strong></td>
  <td>string</td>
  <td>query records with address and operation type(swap/map)</td>
 </tr>
 <tr>
  <td><strong>detail</strong></td>
  <td>string</td>
  <td>test. transaction is in libra chain</td>
 </tr>
 <tr>
  <td><strong>receivers</strong></td>
  <td>string</td>
  <td>query receiver address info</td>
 </tr>
</table>


## Chain - type

**Description**

Describe the chain names can use.

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>btc</strong></td>
  <td>string</td>
  <td>query bitcoin chain record info</td>
 </tr>
 <tr>
  <td><strong>libra</strong></td>
  <td>string</td>
  <td>query libra chain record info</td>
 </tr>
 <tr>
  <td><strong>violas</strong></td>
  <td>string</td>
  <td>query violas chain record info</td>
 </tr>
<table>


## Opttype - type

**Description**

Describe the sub operetion type.

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>swap</strong></td>
  <td>string</td>
  <td>query swap record info, default</td>
 </tr>
 <tr>
  <td><strong>fpswap</strong></td>
  <td>string</td>
  <td>query swap fund proof record info</td>
 </tr>
 <tr>
  <td><strong>map</strong></td>
  <td>string</td>
  <td>query mapping record info</td>
 </tr>
<table>



## Result - type

**Description**

Describe the result struct, json string

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>required/optional</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>state</strong></td>
  <td>string</td>
  <td>required</td>
  <td>request state</td>
 </tr>
 <tr>
  <td><strong>message</strong></td>
  <td>string</td>
  <td>required</td>
  <td>error info</td>
 </tr>
 <tr>
  <td><strong>datas</strong></td>
  <td>string</td>
  <td>required</td>
  <td>datas of result</td>
 </tr>
 <tr>
  <td><strong>sign</strong></td>
  <td>string</td>
  <td>optional</td>
  <td>server signature</td>
 </tr>
 <tr>
  <td><strong>sign_datas</strong></td>
  <td>string</td>
  <td>optional</td>
  <td>datas of sign, hex string of result, format is json.dumps(dict("state":name, "message":message, "datas":datas)).encode().hex() </td>
 </tr>
 <tr>
  <td><strong>sign_key_id</strong></td>
  <td>string</td>
  <td>optional</td>
  <td>md5(sign_public_key)</td>
 </tr>

<table>


## Parameter - list

**Description**

Describe the parameter can use.

### Attributes


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Type</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>opt</strong></td>
  <td><a href="#Opts---type">Opts-type</a></td>
  <td>string</td>
  <td>operation type</td>
 </tr>
 <tr>
  <td><strong>chain</strong></td>
  <td><a href="#Chain---type">Chain-type</a></td>
  <td>string</td>
  <td>query record with chain type</td>
 </tr>
 <tr>
  <td><strong>opttype</strong></td>
  <td><a href="#Opttype---type">Opttype-type</a></td>
  <td>string</td>
  <td>query record with sub opttype</td>
 </tr>
 <tr>
  <td><strong>sender</strong></td>
  <td>address</td>
  <td>string</td>
  <td>abrogation, query record with address</td>
 </tr>
 <tr>
  <td><strong>senders</strong></td>
  <td>address</td>
  <td>string</td>
  <td>query record with addresses. addresses format: address1_chain, address2_chain</td>
 </tr>
 <tr>
  <td><strong>version</strong></td>
  <td>index(1~n)</td>
  <td>int</td>
  <td>query record with version</td>
 </tr>
 <tr>
  <td><strong>cursor</strong></td>
  <td>start</td>
  <td>int</td>
  <td>query record with cursor, default : 0</td>
 </tr>
 <tr>
  <td><strong>limit</strong></td>
  <td>count</td>
  <td>int</td>
  <td>query record with limit, default : 10</td>
 </tr>
 <tr>
  <td><strong>dtype</strong></td>
  <td><a href="https://github.com/palliums-developers/bvexchange/blob/work/docs/map-proto-spec.md#types---type">dtype-type</a></td>
  <td>string</td>
  <td>query record with dtype</td>
 </tr>
</table>



## Records - swap

**Description**

Describe the request swap records.


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>opt</strong></td>
  <td>records</td>
  <td>fixed</td>
 </tr>
 <tr>
  <td><strong>opttype</strong></td>
  <td>swap</td>
  <td>fixed swap</td>
 </tr>
 <tr>
  <td><strong>senders</strong></td>
  <td>address_chain</td>
  <td>count: 1 ~ n; split symbol: ','</td>
 </tr>
 <tr>
  <td><strong>cursor</strong></td>
  <td>0~n</td>
  <td>start index, default: 0</td>
 </tr>
 <tr>
  <td><strong>limit</strong></td>
  <td>1~n</td>
  <td>max count, default: 10</td>
 </tr>
<table>

```
'http://52.231.52.107/?opt=records&senders=4696c44b1b8f7920f98da4863d055fc3_violas&opttype=swap&cursor=0&limit=3'

result: 
{
    "state": SUCCEED,
    "message": "",
    "datas": {
        "count" : int, 
        "cursor" : int, //next record index
        "datas" : [{}, ...]
    }
}
```
 
## Records - fpswap

**Description**

Describe the request swap records.


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>opt</strong></td>
  <td>records</td>
  <td>fixed</td>
 </tr>
 <tr>
  <td><strong>opttype</strong></td>
  <td>fpswap</td>
  <td>fixed fpswap</td>
 </tr>
 <tr>
  <td><strong>senders</strong></td>
  <td>address_chain</td>
  <td>count: 1 ~ n; split symbol: ','</td>
 </tr>
 <tr>
  <td><strong>cursor</strong></td>
  <td>0~n</td>
  <td>start index, default: 0</td>
 </tr>
 <tr>
  <td><strong>limit</strong></td>
  <td>1~n</td>
  <td>max count, default: 10</td>
 </tr>
<table>

```
'http://52.231.52.107/?opt=records&senders=4696c44b1b8f7920f98da4863d055fc3_violas&opttype=fpswap&cursor=0&limit=3'

result: 
{
    "state": SUCCEED,
    "message": "",
    "datas": {
        "count" : int, 
        "cursor" : int, //next record index
        "datas" : [{}, ...]
    }
}
```
 
## Records - map

**Description**

Describe the request mapping records .


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>opt</strong></td>
  <td>records</td>
  <td>fixed</td>
 </tr>
 <tr>
  <td><strong>opttype</strong></td>
  <td>map</td>
  <td>fixed map</td>
 </tr>
 <tr>
  <td><strong>senders</strong></td>
  <td>address_chain</td>
  <td>count: 1 ~ n; split symbol: ','</td>
 </tr>
 <tr>
  <td><strong>cursor</strong></td>
  <td>0~n</td>
  <td>start index, default: 0</td>
 </tr>
 <tr>
  <td><strong>limit</strong></td>
  <td>1~n</td>
  <td>max count, default: 10</td>
 </tr>
<table>

```
'http://52.231.52.107/?opt=records&senders=4696c44b1b8f7920f98da4863d055fc3_violas,2MxBZG7295wfsXaUj69quf8vucFzwG35UWh_btc&opttype=map&cursor=0&limit=5'

result: 
{
    "state": SUCCEED,
    "message': "",
    "datas": {
        "count" : int, 
        "cursor" : int, //next record index
        "datas" : [{}, ...]
    }
}
```


## Receivers - map

**Description**

Describe the request mapping addresses info.


<table>
 <tr>
  <td><strong>Name</strong></td>
  <td><strong>Value</strong></td>
  <td><strong>Description</strong></td>
 </tr>
 <tr>
  <td><strong>opt</strong></td>
  <td>receivers</td>
  <td>fixed</td>
 </tr>
 <tr>
  <td><strong>opttype</strong></td>
  <td>map</td>
  <td>fixed map</td>
 </tr>
<table>

```
'http://52.231.52.107/?opt=receivers&opttype=map'

result: 
{
    "state": SUCCEED,
    "message': "",
    "datas": {
        "datas" : [{}, ...]
    }
    "sign": "...",
    "sign_datas": "...",
    "sign_key_id": "..."
}
```



---




# version list
## v2.0.0
  - append opt = receivers opttype = map | swap
  - append [Result - type](#Result---type): result struct

## v1.0.2
  - modified [Opttype - type](#Opttype---type): added fpswap for fund proof records

## v1.0.1
  - create request-api.md

