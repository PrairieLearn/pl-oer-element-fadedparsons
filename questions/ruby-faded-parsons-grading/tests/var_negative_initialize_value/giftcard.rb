class GiftCard
  attr_reader :balance, :error
  def initialize(balance)
    @balance = balance
    @error = ""
  end
  def withdraw(amount)
    if @balance >= amount
      @balance -= amount
    else
      @error = "Insufficient balance"
      return nil
    end
  end
end
