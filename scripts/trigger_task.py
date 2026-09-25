from worker.tasks import refresh_price

result = refresh_price.delay(product_id=1)
print("Task submitted, id:", result.id)