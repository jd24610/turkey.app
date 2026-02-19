import _sqlite3
import select
__all__ = ['sqlite_version', 'sqlite_version_info', 'sqlite_api_version', 'sqlite_api_version_info', 'connect', 'CompleteException', 'Warning', 'Error', 'InterfaceError', 'DatabaseError', 'DataError', 'OperationalError', 'IntegrityError', 'InternalError', 'ProgrammingError', 'NotSupportedError']
sqlite_version = _sqlite3.sqlite_version
sqlite_version_info = tuple(map(int, sqlite_version.split('.')))
sqlite_api_version = _sqlite3.sqlite_version
sqlite_api_version_info = tuple(map(int, sqlite_api_version.split('.')))
connect = _sqlite3.connect
CompleteException = _sqlite3.CompleteException
Warning = _sqlite3.Warning
Error = _sqlite3.Error
InterfaceError = _sqlite3.InterfaceError            

DatabaseError = _sqlite3.DatabaseError          


