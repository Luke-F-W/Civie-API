# Civie API documentation

This document describes the HTTP API implemented by this repository. The production API base URL is:

```text
https://api.civie.ie
```

All routes below use `GET`. They return JSON, and the endpoints do not require an API key in the application code. Query-string values should be URL-encoded by your HTTP client.

## Quick start

Fetch the first page of Dáil and Seanad composition records:

```text
https://api.civie.ie/API/sector/house?
```

The equivalent `curl` request is:

```sh
curl "https://api.civie.ie/API/sector/house"
```

## Common conventions

### Paginated responses

Most collection endpoints return an object with this shape:

```json
{
  "page": 1,
  "pagesize": 30,
  "records": 123,
  "data": []
}
```

- `page` is the requested, one-based page number. It defaults to `1`.
- `pagesize` is the maximum number of items returned in `data` for that route.
- `records` is the total number of records matching the filters, not just the number on this page.
- `data` contains the records for the requested page. Record fields depend on the dataset; the API adds the key fields listed for each route below.

Use a positive integer for `page`. The API uses the first page when `page` is omitted or cannot be parsed as an integer.

Page sizes are:

| Route/data | Page size |
| --- | ---: |
| Bills, votes, lobbying records, questions, house compositions, and lobbyists | 30 |
| Member list | 15 |
| Debates | 20 |
| Records in a member detail response | 15 per section |

The parties endpoint is not paginated.

### Dates

Routes that accept `after` and `before` filter records by their context date, inclusively. Both values should use `YYYY-MM-DD`. By default, `after` is `1900-01-01` and `before` is `2300-01-01`; an empty value also uses the corresponding default.

### Boolean filters

The include/exclude filters listed below default to `true`, so all categories are included unless you turn one off. Set a filter to `false` to exclude that category. Most routes compare boolean values without regard to case. On the bills route, `SourcePrivate`, `SourceGovernment`, `SourcePrivateMember`, `BillTypePublic`, `BillTypePrivate`, and `BillTypeHybrid` specifically require lowercase `true` or `false`.

Filters on the same route are combined: different filters generally all have to match. Where a single search checks several fields, matching any of those fields is sufficient.

### Text searches

Searches are substring matches. A search term may be URL-encoded; for example, encode spaces as `%20` (or use an HTTP client that encodes query parameters automatically).

## Endpoints

### House composition

```text
GET /API/sector/house
```

Returns paginated Dáil and Seanad composition records. The production response has a `data` array of composition objects, including the chamber composition details, and adds `CompositionPrimaryKey` to each record.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `name` | String | Empty | Exact match against the composition `Name`. |
| `housekey` | String | Empty | Exact match against the composition primary key. |

Example:

```text
https://api.civie.ie/API/sector/house?name=34th%20D%C3%A1il
```

### Members

```text
GET /API/sector/member
```

With no exact-lookup argument, returns a paginated member list ordered by full name. Each member record includes the API-added `memberkey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 15 records per page. |
| `q` | String | Empty | Substring search on the member's full name. |
| `membercode` | String | Empty | Exact match on the member code. Supplying this returns one member object instead of the paginated wrapper. |
| `memberkey` | String | Empty | Exact match on the member ID. Supplying this returns one member object instead of the paginated wrapper. |

`membercode` and `memberkey` can be combined with `q`; all supplied filters must match. If an exact lookup finds no member, the endpoint responds with HTTP `404` and `{"error":"member not found"}`.

Example:

```text
https://api.civie.ie/API/sector/member?q=Mary
```

### Bills

```text
GET /API/sector/bill
```

Returns bills ordered by context date, newest first. Each bill includes the API-added `billkey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `q` | String | Empty | Substring search across English short title, English long title, and Irish short title. |
| `name` | String | Empty | Substring match against the names of members associated with the bill. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date. |
| `before` | Date | `2300-01-01` | Inclusive latest context date. |
| `billkey` | Integer | `0` (no key filter) | Exact match on the bill's database row key. |
| `current` | Boolean | `true` | Include bills with `Current` status. |
| `withdrawn` | Boolean | `true` | Include bills with `Withdrawn` status. |
| `enacted` | Boolean | `true` | Include bills with `Enacted` status. |
| `rejected` | Boolean | `true` | Include bills with `Rejected` status. |
| `defeated` | Boolean | `true` | Include bills with `Defeated` status. |
| `lapsed` | Boolean | `true` | Include bills with `Lapsed` status. |
| `repugnant` | Boolean | `true` | Include bills with `Repugnant` status. |
| `SourcePrivate` | Boolean | `true` | Include bills whose source is `Private`. |
| `SourceGovernment` | Boolean | `true` | Include bills whose source is `Government`. |
| `SourcePrivateMember` | Boolean | `true` | Include bills whose source is `Private Member`. |
| `BillTypePublic` | Boolean | `true` | Include `Public` bills. |
| `BillTypePrivate` | Boolean | `true` | Include `Private` bills. |
| `BillTypeHybrid` | Boolean | `true` | Include `Hybrid` bills. |

The source and type argument names are case-sensitive and their boolean values must be lowercase. For example, `SourceGovernment=false` excludes government bills.

Example:

```text
https://api.civie.ie/API/sector/bill?after=2024-01-01&before=2024-12-31&enacted=false
```

### Votes

```text
GET /API/sector/vote
```

Returns votes ordered by context date, newest first. Each vote includes the API-added `votekey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `q` | String | Empty | Substring search in vote text and the names of members recorded as voting for, against, or abstaining. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date. |
| `before` | Date | `2300-01-01` | Inclusive latest context date. |
| `votekey` | String | Empty | Exact match on the vote primary key. |
| `dail` | Boolean | `true` | Include Dáil Éireann votes. |
| `seanad` | Boolean | `true` | Include Seanad Éireann votes. |
| `committee` | Boolean | `true` | Include votes outside those two chambers. Set to `false` to limit results to Dáil and Seanad votes. |
| `lost` | Boolean | `true` | Include votes with outcome `Lost`. |
| `carried` | Boolean | `true` | Include votes with outcome `Carried`. |
| `null` | Boolean | `true` | Include votes with no recorded outcome (stored as `_`). |

The three chamber filters are independent. For example, `dail=false&seanad=false&committee=true` selects votes from other chambers; setting all three to `false` returns no votes.

### Debates

```text
GET /API/sector/debate
```

Returns debates ordered by context date, newest first. Each debate includes the API-added `debatekey`. The page size is 20.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 20 records per page. |
| `q` | String | Empty | Substring search in debate titles or the serialized debate record. |
| `name` | String | Empty | Substring match against member names or member codes. |
| `debatetitles` | String | Empty | Substring match against debate titles. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date. |
| `before` | Date | `2300-01-01` | Inclusive latest context date. |
| `debatekey` | String | Empty | Exact match on the debate ID. |
| `dail` | Boolean | `true` | Include Dáil debates. |
| `seanad` | Boolean | `true` | Include Seanad debates. |
| `committee` | Boolean | `true` | Include debates outside the Dáil and Seanad. Set to `false` to limit results to those two houses. |

The chamber filters work like the vote filters: setting all of `dail`, `seanad`, and `committee` to `false` returns no debates.

### Lobbying records

```text
GET /API/sector/lobby
```

Returns lobbying records ordered by context date, newest first. Each record includes the API-added `lobbyingkey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `q` | String | Empty | Substring search across lobbyist names, main lobbyist, member codes, relevant matter, details, subject matter, lobbying activities, and intended results. |
| `lobbyistcode` | String | Empty | Exact match on lobbyist code. |
| `lobbyingkey` | String | Empty | Exact match on the lobbying record primary key. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date. |
| `before` | Date | `2300-01-01` | Inclusive latest context date. |

### Questions

```text
GET /API/sector/question
```

Returns questions ordered by context date, newest first. Each question includes the API-added `questionkey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `q` | String | Empty | Substring search in question text or answer text. |
| `questiontxt` | String | Empty | Substring search in question text. |
| `answertxt` | String | Empty | Substring search in answer text. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date. |
| `before` | Date | `2300-01-01` | Inclusive latest context date. |
| `questionkey` | String | Empty | Exact match on the question primary key. |
| `oral` | Boolean | `true` | Include oral questions. |
| `written` | Boolean | `true` | Include written questions. |

When `q`, `questiontxt`, and/or `answertxt` are supplied together, every supplied search filter must match. Within `q`, a match in either the question or answer text is sufficient.

### Lobbyists

```text
GET /API/sector/lobbyist
```

Returns lobbyists ordered by their tally, highest first. Each record includes the API-added `lobbyistkey`.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number; 30 records per page. |
| `q` | String | Empty | Substring search in lobbyist name or lobbyist code. |
| `lobbyistcode` | String | Empty | Exact match on lobbyist code. |
| `lobbyistkey` | String | Empty | Exact match on the lobbyist primary key. |

### Parties

```text
GET /API/sector/party
```

Returns all party records, ordered by party code. This route takes no query arguments and is not paginated. The response has `records` (the number of parties) and `data` (the party records).

### Member activity and statistics

```text
GET /API/<member_code>
```

Replace `<member_code>` with a member code. The response combines the matching member record, where available, with bills, votes, debates, lobbying records, questions, and member statistics. The `member`, `stats`, and individual activity records contain the fields supplied by their datasets; activity records also receive their corresponding API key (`billkey`, `votekey`, `debatekey`, `lobbyingkey`, or `questionkey`).

Each activity section is independently paginated, with 15 records per section. The same `page` applies to every section. Activity sections have their own `page`, `pagesize`, `records`, and `data` properties. The top-level `member` and `stats` properties are present when matching data is available.

| Argument | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | Integer | `1` | Page number for each activity section; 15 records per section. |
| `q` | String | Empty | Substring search in each activity record's serialized JSON. |
| `after` | Date | `1900-01-01` | Inclusive earliest context date for activity records. |
| `before` | Date | `2300-01-01` | Inclusive latest context date for activity records. |
| `memberkey` | String | Empty | Member database ID; when it matches a member, the API resolves it to that member's code. |

Example:

```text
https://api.civie.ie/API/TD123?after=2024-01-01&page=1
```

Replace `TD123` with the desired member code. This route returns empty activity sections when no matching activity is found; it does not use the single-member `404` behavior of `/API/sector/member`.

## Operational notes

- The application configures a rate limit of 720 requests per hour per client IP. Requests over the limit may receive HTTP `429 Too Many Requests`.
- Responses are cached by the API for a short period. Most filtered endpoints include the query string in their cache key, so different filters have separate cached responses.
- The member, bill, vote, debate, lobbying, question, party, house, and lobbyist routes expose the data available in the server's database. Available records and record fields can change as that data is maintained.
