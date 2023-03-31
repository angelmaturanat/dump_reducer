# dump_reducer
This script allows reducing the dump size, removing the unnecessary data indicated by the user. Currently, I have a serious problem using version-based databases because they are so big and the versioned information is not necessary for me. For that reason I create this script to reduce the database size removing the versioned or logic deleted data.


## Requirements:

- Python: 3.*
- PIP Dependencies:
  - mysql-connector-python

## Getting Started

### Requeriments
Firstly we must install the python dependencies using this command:

```SH
$ pip install -r requirements.txt
```

### Understanding the logic behind
This script creates a rules file to know and run your own database migration logic using the database name indicated by params.

The rules file has the following structure:
```JSON
[
    {
        "table": "<YOUR TABLE>",
        "raw_source": null,
        "condition": null,
        "priority_number": null
    }
]
```

And each field means:
- `table`: Table to apply the logic
- `raw_source`: This rule allows us to add the custom table fields to be migrated. It is used to indicate a custom logic in a table column (ISNULL, IF, etc.).
- `condition`: Is a condition to migrate the information. This field could be an `INNER JOIN` or `WHERE` statement.
- `priority_number`: This column is so important, using this field we could indicate the priority migration to respect the table's dependence.


A little example:
```JSON
    {
        "table": "groups",
        "raw_source": "(id, code, enabled, created_at, updated_at) SELECT * FROM groups",
        "condition": "WHERE enabled = true",
        "priority_number": 1
    }
```

### Usage
We need to create two important files that allow us generate the correct logic to reduce the database size. To do that you must run these commands:

#### Rules file generation
You need use this command to generate the rules file in where we can indicate custom logic to filter the information that we need to migrate. For example the most common filter is the `enabled` table column in true to migrate only the active information. We havve two different posibilities to generate this file:

1. Simple file without table conditions:
```SH
python rules_creator.py --host='<YOUR DB HOST>' --username='<YOUR DB USER>' --password='<YOUR DB PASSWORD>' --port='<YOUR DB PORT>' --database='<YOUR TARGET DB>'
```

2. Rules file but including a default condition for all tables, for example the `enabled` column filter:
```SH
python rules_creator.py --host='<YOUR DB HOST>' --username='<YOUR DB USER>' --password='<YOUR DB PASSWORD>' --port='<YOUR DB PORT>' --database='<YOUR TARGET DB>' --condition='WHERE enabled = true'
```

Now you should see the `rules.json` file in the root directory.


#### Dump generation
This command creates the database replication structure in where our data will be migrated and immediatry begins to migrate the information using the rules file logic:

```SH
$ python main.py --host='<YOUR DB HOST>' --username='<YOUR DB USER>' --password='<YOUR DB PASSWORD>' --port='<YOUR DB PORT>' --database='<YOUR TARGET DB>'
```


