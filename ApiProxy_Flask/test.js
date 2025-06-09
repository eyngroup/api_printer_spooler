function calculateTwoNumbers(num1, num2) {
  const sum = num1 + num2;
  const difference = num1 - num2;
  const product = num1 * num2;
  const quotient = num1 / num2;

  return { sum, difference, product, quotient };
}

const result = calculateTwoNumbers(5, 3);

console.log(`The sum is ${result.sum}`);
console.log(`The difference is ${result.difference}`);
console.log(`The product is ${result.product}`);
console.log(`The quotient is ${result.quotient}`);
