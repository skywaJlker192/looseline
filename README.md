# Таблица методов модуля ставок и расчётов

| № | Название метода | Назначение | Статус |
|---|----------------|------------|--------|
| 1 | `calculatePotentialWin(amount, coefficient)` | Рассчитывает потенциальный выигрыш и прибыль для одиночной ставки. Формула: `payout = amount * coefficient`, `profit = payout - amount`. Используется в реальном времени при вводе суммы ставки для отображения в блоке "Потенциальный выигрыш". |  Реализован (frontend) |
| 2 | `placeBet(payload)` | Размещает ставку пользователя. Принимает объект с `eventId`, `outcome`, `coefficient`, `amount`. Имитирует сетевой запрос с задержкой 400ms и возвращает объект с `betId`. В реальном приложении должен вызывать backend API `POST /api/bets/place`. |  Реализован (frontend mock) |
| 3 | `createCoupon(betIds, totalAmount)` | Создаёт купон (экспресс) из нескольких ставок. Генерирует уникальный код купона (формат: `CPN20251215_ABC123`). Возвращает `couponId`, `couponCode`, `totalBetAmount`, `numberOfBets`. В реальном приложении должен вызывать backend API `POST /api/coupons/create`. |  Реализован (frontend mock) |
| 4 | `updateBetStatus(betId, newStatus, reason)` | Обновляет статус ставки (open → cancelled/resolved). При отмене возвращает информацию о возврате денег (`refundAmount`, `transactionType: 'bet_cancelled'`). В реальном приложении должен вызывать backend API `PATCH /api/bets/:betId/status`. |  Реализован (frontend mock) |
| 5 | `calculatePotentialWinCoupon(amount, coefficients[])` | Расчёт потенциального выигрыша для купона (экспресса). Принимает массив коэффициентов, вычисляет общий коэффициент как произведение всех коэффициентов, затем рассчитывает `potential_win = amount * total_coefficient`. Автоматически фильтрует невалидные коэффициенты (< 1.01). |  Реализован (frontend) |

---

## Детали реализации

### Метод 1: `calculatePotentialWin`
**Файл:** `src/bets/services/betService.js`  
**Использование:** Вызывается автоматически через `useMemo` в `BetSlipContext` при изменении суммы или коэффициента.  
**Пример:**
```javascript
const { payout, profit } = calculatePotentialWin(100, 1.85)
// payout = 185.00, profit = 85.00
```

### Метод 2: `placeBet`
**Файл:** `src/bets/services/betService.js`  
**Использование:** Вызывается при клике на кнопку "Подтвердить" в модальном окне подтверждения ставки (`BetConfirmationModal`).  
**Пример:**
```javascript
const result = await placeBet({
  eventId: '1',
  outcome: 'HOME',
  coefficient: 1.85,
  amount: 100
})
// result = { betId: 'ABC123XYZ' }
```

### Метод 3: `createCoupon`
**Файл:** `src/bets/services/betService.js`  
**Использование:** Вызывается для создания купона из нескольких уже размещённых ставок.  
**Пример:**
```javascript
const result = await createCoupon(['bet1', 'bet2', 'bet3'], 150)
// result = {
//   couponId: 'ABC123',
//   couponCode: 'CPN20251215_XYZ789',
//   totalBetAmount: 150,
//   numberOfBets: 3
// }
```

### Метод 4: `updateBetStatus`
**Файл:** `src/bets/services/betService.js`  
**Использование:** Вызывается при отмене ставки пользователем или при отмене события администратором.  
**Пример:**
```javascript
// Отмена ставки
const result = await updateBetStatus('bet123', 'cancelled', 'Передумал')
// result = {
//   success: true,
//   betId: 'bet123',
//   status: 'cancelled',
//   refundAmount: null, // На backend будет реальная сумма
//   transactionType: 'bet_cancelled'
// }

// Повторное открытие ставки
await updateBetStatus('bet123', 'open', 'Ставка открыта заново')
```

### Метод 5: `calculatePotentialWinCoupon`
**Файл:** `src/bets/services/betService.js`  
**Использование:** Вызывается для расчёта потенциального выигрыша купона перед его созданием.  
**Пример:**
```javascript
const result = calculatePotentialWinCoupon(150, [1.85, 2.1, 3.4])
// result = {
//   betAmount: 150,
//   coefficients: [1.85, 2.1, 3.4],
//   totalCoefficient: 13.21,
//   potentialWin: 1981.35,
//   profit: 1831.35
// }
```

---

## Тестирование

Все реализованные методы покрыты тестами:
-  `betService.test.js` — юнит-тесты для всех 5 методов:
  - `calculatePotentialWin` — 3 теста (валидные данные, граничные случаи, NaN)
  - `placeBet` — 1 тест (возврат betId, проверка задержки)
  - `calculatePotentialWinCoupon` — 4 теста (расчёт для 3 ставок, пустой массив, фильтрация невалидных коэффициентов, одна ставка)
  - `createCoupon` — 4 теста (создание купона, валидация пустого массива, валидация суммы, уникальность кодов)
  - `updateBetStatus` — 5 тестов (отмена, открытие, невалидный статус, отсутствие betId, без reason)
-  `BetFlow.test.jsx` — интеграционные UI-тесты для полного флоу размещения ставки

