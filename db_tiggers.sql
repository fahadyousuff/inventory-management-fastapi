-- Database Trigger for reducing Stock from Product Master table, when sale has been posted
CREATE TRIGGER reduce_stock_after_sales
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
	UPDATE product
	SET Stock = Stock - NEW.Quantity
	WHERE Id = NEW.ProductId;
end;