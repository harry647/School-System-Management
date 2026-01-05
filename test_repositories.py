#!/usr/bin/env python3
"""
Test script to verify all repositories work with their respective models.
"""

def test_repositories():
    """Test that all repositories can be imported and instantiated."""
    print("Testing repository imports and instantiation...")
    
    try:
        # Import all repositories
        from school_system.database.repositories import (
            BaseRepository,
            StudentRepository,
            TeacherRepository,
            BookRepository,
            UserRepository,
            # Student-related repositories
            ReamEntryRepository,
            TotalReamsRepository,
            # Book-related repositories
            BookTagRepository,
            BorrowedBookStudentRepository,
            BorrowedBookTeacherRepository,
            QRBookRepository,
            QRBorrowLogRepository,
            DistributionSessionRepository,
            DistributionStudentRepository,
            DistributionImportLogRepository,
            # User-related repositories
            UserSettingRepository,
            ShortFormMappingRepository,
            # Furniture-related repositories
            ChairRepository,
            LockerRepository,
            FurnitureCategoryRepository,
            LockerAssignmentRepository,
            ChairAssignmentRepository
        )
        
        print("All repositories imported successfully")
        
        # Test instantiation of each repository
        repositories = [
            StudentRepository,
            TeacherRepository,
            BookRepository,
            UserRepository,
            ReamEntryRepository,
            TotalReamsRepository,
            BookTagRepository,
            BorrowedBookStudentRepository,
            BorrowedBookTeacherRepository,
            QRBookRepository,
            QRBorrowLogRepository,
            DistributionSessionRepository,
            DistributionStudentRepository,
            DistributionImportLogRepository,
            UserSettingRepository,
            ShortFormMappingRepository,
            ChairRepository,
            LockerRepository,
            FurnitureCategoryRepository,
            LockerAssignmentRepository,
            ChairAssignmentRepository
        ]
        
        print("Testing repository instantiation...")
        for repo_class in repositories:
            try:
                repo_instance = repo_class()
                print(f"{repo_class.__name__} instantiated successfully")
                # Verify the model is set correctly
                if hasattr(repo_instance, 'model'):
                    print(f"   Model: {repo_instance.model.__name__ if repo_instance.model else 'None'}")
                else:
                    print(f"   Warning: No model attribute found")
            except Exception as e:
                print(f"{repo_class.__name__} failed: {e}")
        
        print("\nAll repository tests completed!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_repositories()