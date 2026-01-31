from sqlalchemy.orm import Session
from database import SessionLocal
from models import Organization, Building, Activity, Phone

db: Session = SessionLocal()


def init_data():
    buildings = [
        Building(address="г. Москва, ул. Блюхера, 32/1", latitude=55.7558, longitude=37.6173),
        Building(address="г. Москва, ул. Ленина, 1, офис 3", latitude=55.7520, longitude=37.6156),
        Building(address="г. Санкт-Петербург, Невский проспект, 28", latitude=59.9343, longitude=30.3351),
        Building(address="г. Москва, ул. Тверская, 10", latitude=55.7558, longitude=37.6175),
    ]
    
    for building in buildings:
        db.add(building)
    db.commit()
    
    food = Activity(name="Еда", parent_id=None)
    db.add(food)
    db.flush()
    
    cars = Activity(name="Автомобили", parent_id=None)
    db.add(cars)
    db.flush()
    
    meat = Activity(name="Мясная продукция", parent_id=food.id)
    db.add(meat)
    db.flush()
    
    dairy = Activity(name="Молочная продукция", parent_id=food.id)
    db.add(dairy)
    db.flush()
    
    cargo = Activity(name="Грузовые", parent_id=cars.id)
    db.add(cargo)
    db.flush()
    
    passenger = Activity(name="Легковые", parent_id=cars.id)
    db.add(passenger)
    db.flush()
    
    parts = Activity(name="Запчасти", parent_id=cars.id)
    db.add(parts)
    db.flush()
    
    accessories = Activity(name="Аксессуары", parent_id=parts.id)
    db.add(accessories)
    db.commit()
    
    phones_data = [
        "2-222-222",
        "3-333-333",
        "4-444-444",
        "5-555-555",
        "6-666-666",
        "7-777-777",
    ]
    
    phones = []
    for phone_num in phones_data:
        phone = Phone(number=phone_num)
        db.add(phone)
        phones.append(phone)
    db.commit()
    
    org1 = Organization(
        name='ООО "Рога и Копыта"',
        building_id=buildings[0].id
    )
    org1.phones = [phones[0], phones[1]]
    org1.activities = [meat, dairy]
    db.add(org1)
    
    org2 = Organization(
        name='ООО "Молочный мир"',
        building_id=buildings[1].id
    )
    org2.phones = [phones[2]]
    org2.activities = [dairy]
    db.add(org2)
    
    org3 = Organization(
        name='ООО "АвтоСервис"',
        building_id=buildings[2].id
    )
    org3.phones = [phones[3], phones[4]]
    org3.activities = [cargo, passenger, parts]
    db.add(org3)
    
    org4 = Organization(
        name='ООО "Мясной ряд"',
        building_id=buildings[0].id
    )
    org4.phones = [phones[5]]
    org4.activities = [meat]
    db.add(org4)
    
    org5 = Organization(
        name='ООО "АвтоАксессуары"',
        building_id=buildings[3].id
    )
    org5.phones = [phones[0]]
    org5.activities = [accessories]
    db.add(org5)
    
    db.commit()
    print("Тестовые данные успешно добавлены в базу данных!")


if __name__ == "__main__":
    try:
        existing_buildings = db.query(Building).count()
        if existing_buildings > 0:
            print("База данных уже содержит данные. Пропускаем инициализацию.")
        else:
            init_data()
    except Exception as e:
        print(f"Ошибка при инициализации данных: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

