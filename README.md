# Таблица методов модуля ставок и расчётов

| № | Название метода | Назначение | Статус |
|---|----------------|------------|--------|
| 1 | `calculatePotentialWin(amount, coefficient)` | Рассчитывает потенциальный выигрыш и прибыль для одиночной ставки. Формула: `payout = amount * coefficient`, `profit = payout - amount`. Используется в реальном времени при вводе суммы ставки для отображения в блоке "Потенциальный выигрыш". |  Реализован (frontend) |
| 2 | `placeBet(payload)` | Размещает ставку пользователя. Принимает объект с `eventId`, `outcome`, `coefficient`, `amount`. Имитирует сетевой запрос с задержкой 400ms и возвращает объект с `betId`. В реальном приложении должен вызывать backend API `POST /api/bets/place`. |  Реализован (frontend mock) |
| 3 | `createCoupon(betIds, totalAmount)` | Создаёт купон (экспресс) из нескольких ставок. Рассчитывает общий коэффициент как произведение всех коэффициентов ставок в купоне. Купон выигрывает только если ВСЕ ставки выигрывают. | ⏳ Планируется (backend) |
| 4 | `updateBetStatus(betId, newStatus, reason)` | Обновляет статус ставки (open → cancelled/resolved). При отмене возвращает деньги на баланс пользователя и записывает транзакцию типа `bet_cancelled`. Используется при отмене ставки пользователем или при отмене события администратором. |  Планируется (backend) |
| 5 | `calculatePotentialWinCoupon(amount, coefficients[])` | Расчёт потенциального выигрыша для купона (экспресса). Принимает массив коэффициентов, вычисляет общий коэффициент как произведение всех коэффициентов, затем рассчитывает `potential_win = amount * total_coefficient`. |  Планируется (frontend/backend) |

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

---

## Тестирование

Все реализованные методы покрыты тестами:
-  `betService.test.js` — юнит-тесты для `calculatePotentialWin` и `placeBet`
-  `BetFlow.test.jsx` — интеграционные UI-тесты для полного флоу размещения ставки

