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




-- Database Trigger for adjusting negative stock on insert
CREATE TRIGGER prevent_negative_stock_on_insert
BEFORE INSERT ON sales
FOR EACH ROW
WHEN (SELECT Stock FROM product WHERE Id = NEW.ProductId) < NEW.Quantity
BEGIN
    SELECT RAISE(ABORT, 'Insufficient stock for this sale.');
END;




-- Database Trigger for adjusting negative stock on update
CREATE TRIGGER prevent_negative_stock_on_update
BEFORE UPDATE ON sales
FOR EACH ROW
WHEN (
    -- Case A: same product → stock + old qty must cover new qty
    (NEW.ProductId = OLD.ProductId
     AND (SELECT Stock FROM product WHERE Id = NEW.ProductId) + OLD.Quantity < NEW.Quantity)
    OR
    -- Case B: different product → new product's current stock must cover new qty
    (NEW.ProductId != OLD.ProductId
     AND (SELECT Stock FROM product WHERE Id = NEW.ProductId) < NEW.Quantity)
)
BEGIN
    SELECT RAISE(ABORT, 'Insufficient stock for this update.');
END;
