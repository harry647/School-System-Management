from typing import List, Optional, Type, TypeVar, Generic
from contextlib import contextmanager
from ...core.exceptions import DatabaseException
from ...core.validators import StudentValidator, TeacherValidator, BookValidator, UserValidator

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class implementing CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
        self._db = None  # Lazy initialization
    
    @property
    def db(self):
        """Lazy import database connection to avoid circular imports."""
        if self._db is None:
            from ..connection import get_db_session
            self._db = get_db_session()
        return self._db
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by primary key."""
        try:
            cursor = self.db.cursor()
            pk = getattr(self.model, '__pk__', 'id')
            cursor.execute(f"SELECT * FROM {self.model.__tablename__} WHERE {pk} = ?", (id,))
            result = cursor.fetchone()
            if result:
                return self.model(**dict(zip([column[0] for column in cursor.description], result)))
            return None
        except Exception as e:
            raise DatabaseException(f"Error retrieving entity by ID: {e}")

    def get_all(self) -> List[T]:
        """Get all entities."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {self.model.__tablename__}")
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error retrieving all entities: {e}")

    def create(self, entity=None, **kwargs) -> T:
        """Create a new entity."""
        try:
            if entity is not None:
                kwargs = vars(entity)
            # Exclude updated_at and created_at if present, as most tables don't have them
            kwargs = {k: v for k, v in kwargs.items() if k not in ['updated_at', 'created_at']}
            cursor = self.db.cursor()
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?'] * len(kwargs))
            cursor.execute(f"INSERT INTO {self.model.__tablename__} ({columns}) VALUES ({placeholders})", tuple(kwargs.values()))
            self.db.commit()
             
            # Retrieve the auto-generated ID for models that have auto-increment primary keys
            pk = getattr(self.model, '__pk__', None)
            # Note: student_id is not auto-increment in the current schema, it's TEXT PRIMARY KEY
            # So we don't need to set it from lastrowid
             
            return self.model(**kwargs)
        except Exception as e:
            raise DatabaseException(f"Error creating entity: {e}")

    def update(self, entity) -> Optional[T]:
        """Update an existing entity."""
        try:
            cursor = self.db.cursor()
            # Get the primary key value from the entity
            pk = getattr(self.model, '__pk__', 'id')
            pk_value = getattr(entity, pk)
            
            # Get all attributes of the entity except the primary key, created_at, and updated_at
            kwargs = {k: v for k, v in vars(entity).items() if k not in [pk, 'created_at', 'updated_at']}
            
            set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            cursor.execute(f"UPDATE {self.model.__tablename__} SET {set_clause} WHERE {pk} = ?", (*kwargs.values(), pk_value))
            self.db.commit()
            return self.get_by_id(pk_value)
        except Exception as e:
            raise DatabaseException(f"Error updating entity: {e}")

    def delete(self, id: int) -> bool:
        """Delete an entity."""
        try:
            cursor = self.db.cursor()
            pk = getattr(self.model, '__pk__', 'id')
            cursor.execute(f"DELETE FROM {self.model.__tablename__} WHERE {pk} = ?", (id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseException(f"Error deleting entity: {e}")

    def find_by_field(self, field_name: str, value) -> List[T]:
        """Find entities by a specific field."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {self.model.__tablename__} WHERE {field_name} = ?", (value,))
            results = cursor.fetchall()
            return [self.model(**dict(zip([column[0] for column in cursor.description], row))) for row in results]
        except Exception as e:
            raise DatabaseException(f"Error finding entities by field: {e}")

    def count(self) -> int:
        """Count all entities."""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.model.__tablename__}")
            return cursor.fetchone()[0]
        except Exception as e:
            raise DatabaseException(f"Error counting entities: {e}")

    def exists(self, **conditions) -> bool:
        """Check if a record exists with given conditions."""
        try:
            cursor = self.db.cursor()
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            cursor.execute(
                f"SELECT 1 FROM {self.model.__tablename__} WHERE {where_clause} LIMIT 1",
                tuple(conditions.values())
            )
            return cursor.fetchone() is not None
        except Exception as e:
            raise DatabaseException(f"Error checking existence: {e}")

    def get_by_fields(self, **conditions) -> Optional[T]:
        """Get a single entity by multiple fields."""
        try:
            cursor = self.db.cursor()
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            cursor.execute(
                f"SELECT * FROM {self.model.__tablename__} WHERE {where_clause} LIMIT 1",
                tuple(conditions.values())
            )
            row = cursor.fetchone()
            if row:
                return self.model(**dict(zip([c[0] for c in cursor.description], row)))
            return None
        except Exception as e:
            raise DatabaseException(f"Error retrieving entity by fields: {e}")

    def bulk_create(self, rows: List[dict]) -> int:
        """Insert multiple rows efficiently."""
        if not rows:
            return 0
        try:
            cursor = self.db.cursor()
            columns = rows[0].keys()
            placeholders = ', '.join(['?'] * len(columns))
            sql = f"""
                INSERT INTO {self.model.__tablename__}
                ({', '.join(columns)})
                VALUES ({placeholders})
            """
            cursor.executemany(
                sql,
                [tuple(row[col] for col in columns) for row in rows]
            )
            self.db.commit()
            return cursor.rowcount
        except Exception as e:
            raise DatabaseException(f"Error bulk creating entities: {e}")

    def bulk_update(self, updates: List[dict], where_field: str):
        """
        Bulk update rows.
        Each dict must contain `where_field`.
        """
        try:
            cursor = self.db.cursor()
            for row in updates:
                where_value = row.pop(where_field)
                set_clause = ', '.join([f"{k} = ?" for k in row.keys()])
                cursor.execute(
                    f"""
                    UPDATE {self.model.__tablename__}
                    SET {set_clause}
                    WHERE {where_field} = ?
                    """,
                    (*row.values(), where_value)
                )
            self.db.commit()
        except Exception as e:
            raise DatabaseException(f"Error bulk updating entities: {e}")

    def delete_by_fields(self, **conditions) -> int:
        """Delete rows matching conditions."""
        try:
            cursor = self.db.cursor()
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            cursor.execute(
                f"DELETE FROM {self.model.__tablename__} WHERE {where_clause}",
                tuple(conditions.values())
            )
            self.db.commit()
            return cursor.rowcount
        except Exception as e:
            raise DatabaseException(f"Error deleting by fields: {e}")

    def paginate(self, limit: int, offset: int = 0) -> List[T]:
        """Paginated retrieval."""
        try:
            cursor = self.db.cursor()
            cursor.execute(
                f"SELECT * FROM {self.model.__tablename__} LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [
                self.model(**dict(zip([c[0] for c in cursor.description], row)))
                for row in rows
            ]
        except Exception as e:
            raise DatabaseException(f"Error paginating entities: {e}")

    @contextmanager
    def transaction(self):
        """Transaction context manager for atomic operations."""
        try:
            yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

