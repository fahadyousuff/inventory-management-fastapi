-- ========================== POST Method ================================

-- Database Trigger for reducing Stock from Product Master table, when sale has been POSTED
CREATE TRIGGER reduce_stock_after_sales
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
	UPDATE product
	SET Stock = Stock - NEW.Quantity
	WHERE Id = NEW.ProductId;
end;


-- ========================== PUT Method ================================

-- Database Trigger for adjusting Stock from Product Master table, when sale transaction has been UPDATED
CREATE TRIGGER adjust_stock_after_sales_update
AFTER UPDATE ON sales
FOR EACH ROW
BEGIN
	UPDATE product
	SET Stock = Stock + OLD.Quantity
	WHERE Id = OLD.ProductId;
	
	UPDATE product
	SET Stock = Stock - NEW.Quantity
	WHERE Id = NEW.ProductId;
END;


-- ========================== PUT Method ================================

-- Database Trigger for adjusting Stock from Product Master table, when sale transaction has been DELETED
CREATE TRIGGER adjust_stock_after_sales_delete
AFTER DELETE ON sales
FOR EACH ROW
BEGIN
	UPDATE product
	SET Stock = Stock + OLD.Quantity
	WHERE Id = OLD.ProductId;
END;
