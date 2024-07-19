// task1.js
function editItem(index) {
    const item = items[index];
    document.getElementById('itemName').value = item.itemName;
    document.getElementById('itemId').value = item.itemId;
    document.getElementById('date').value = item.date;
    document.getElementById('batchNo').value = item.batchNo;
    document.getElementById('price').value = item.price;
    document.getElementById('editIndex').value = index;
}
