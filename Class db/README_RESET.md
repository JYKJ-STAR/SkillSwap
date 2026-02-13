# Database Reset Instructions

## Reset All (Users + Admins)
```
venv\Scripts\python.exe "Class db/reset_database.py"
```

## Reset Users Only
```
venv\Scripts\python.exe "Class db/reset_database.py" --users
```

## Reset Admins Only
```
venv\Scripts\python.exe "Class db/reset_database.py" --admins
```

## Reset Events (Restore Seed Data as Published)

**Use this to restore default event cards that appear in the Approved admin page and show to users!**

```
venv\Scripts\python.exe "Class db/reset_database.py" --events
```