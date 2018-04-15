# MMfSDT/network-tests
Companion repository to `MMfSDT/mininet-topo-generator` to provide testing, data extraction and data processing. Focuses on getting Flow Completion Time (FCT) and Throughput for all host pairs in a given topology described on the generator. 

## Repository Structure
```
./
|-- logs/
    |-- pcaps/
        |-- ...
    |-- aggregate.json
    |-- ...
|-- postprocess.py
|-- README.md
|-- test.py
|-- ...
```

where `test.py` is meant to be run within the Mininet topology (i.e., with `--test`) and `postprocess.py` is meant to be run outside the Mininet topology (i.e., with `--post`). In addition, the `logs/` directory, as described later, will contain all executed test results (in a JSON-formatted array inside `logs/aggregate.json`) and all `.pcap` backups (in `logs/pcaps/`).

## Configuration
Follow the `Prerequisites and Dependencies` given at [`MMfSDT/mininet-topo-generator`](https://github.com/MMfSDT/mininet-topo-generator/blob/master/README.md#prerequisites-and-dependencies). In addition, make sure to place the `network-tests` and `mininet-topo-generator` repositories in one directory.

## Running `test.py` and `postprocessing.py`
The script can be run either at launch of the `mininet-topo-generator` or within the Mininet CLI itself. 

### `mininet-topo-generator`
The instructions below assume that you are currently within the root directory of the `mininet-topo-generator` repository.

#### Both test and post-processing

If you want to run both test and post-processing, run the following snippet. Note that `--pcap` is required when `--post` is specified.
```bash
sudo ./run.sh --test ../network-tests/test.py --post ../network-tests/test.py --pcap # Add other parameters here
```

This will output a file `aggregate.json` with a JSON object containing your test results (both FCT and Througput).

#### Test only

If you want to run a test without post-processing, run the following snippet.
```bash
sudo ./run.sh --test ../network-tests/test.py # Add other parameters here
```

This will output a file `mid.json` with a JSON object containing your test results (Throughput only).

#### Additional Options and Instructions

Additional instructions are available at ['MMfSDT/mininet-topo-generator'](https://github.com/MMfSDT/mininet-topo-generator/blob/master/README.md#running-the-script) under `Running the Script`.

### Within the Mininet CLI
If for some reason you want to manually enable the script/want to create your own, edit `commands.txt` to your liking (with valild Mininet commands), then source the file.

```bash
sudo ./run.sh # Add --post and/or --pcap if you want FCT postprocessing/pcap logging.
source ../network-tests/commands.txt
```

## Convention
To recap, the following arguments will be used for launching tests.

```javascript
{
    "K": int | [2, {4}, 8, 16, 32, 64, 128],
    "router": string | [{static}, ecmp, ps],
    "proto": string | [tcp, {mptcp}],
    "pmanager": string | [{fullmesh}, ndiffports],
    "diffports": int | [1 - 16],
    "payloadsize": string | [query, long, {short}],
    "runcount": int | [{5}],
    "mode": string | [{onetoone}, onetomany],
    "juggler": boolean | [{false}],
    ...
}
```

where `query` messages are `10kB`, `short` `500kB`, and `long` `25MB`.

By default, tests will be run on `mptcp-fullmesh` with a `runcount` of `5` on `k=4` with a payload size of `500kB`.

More details are available at [`MMfSDT/mininet-topo-generator/README.md`](https://github.com/MMfSDT/mininet-topo-generator/blob/master/README.md#running-the-script).

## Logs
The logs directory will be structured as follows:

```bash
logs/
|-- pcaps/
    |-- pcap-*/
    |-- foo
|-- aggregate.db
|-- args.txt
|-- foo
|-- mid.json
```

where,
* `logs/pcaps` have the `.pcap` backups for all executed tests for debugging/archival purposes.
* `logs/pcaps/pcap-*/` will be the directory naming convention per test, where the `*` is a Unix timestamp.
* `logs/aggregate.db` will contain all previously executed tests, in an SQLite3 database. This will serve as the output of `postprocess.py`. In the future, this will be the main source of data for visualization.
* `logs/args.txt` will contain the arguments/metadata used by both `test.py` and `postprocess.py` (mentioned in `Conventions`) in a .json object.
* `logs/mid.json` will serve as the output of `test.py` (JSON object), containing only throughput data. FCT will then be extracted from the `.pcap` logs through post-processing, and the final JSON object will be appended to `aggregate.json`
* `foo` are placeholder files to ensure that the directories won't be skipped.

### `args.txt` JSON format
> Used by: `test.py`, `postprocess.py`

See [`Conventions`]() above.
### `mid.json` JSON format
> Output of: `test.py`; Used by: `postprocess.py`
```javascript
[
    {
        "serverName": string | `/h\d\d\d`,
        "serverIP": string | `10.\d+.\d+.\d+`,
        "clientName": string | `/h\d\d\d`,
        "clientIP": string | `10.\d+.\d+.\d+`,
        "run": int
    }
]
```

`mid.json` then contains an array of server-client pair results specified in the format above (i.e., for a `K = 4` topology, expect the array length to be `num_hosts = K^3/4 = 16`).
