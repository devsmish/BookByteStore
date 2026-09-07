def print_books(book_list):
    if not book_list:
        print("No books available.")
        return
    for i, book in enumerate(book_list, 1):
        print(f"{i}. {book.title} by {book.author} - ${book.price} ({book.stock} in stock)")
