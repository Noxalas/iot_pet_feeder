# Automatic IoT Pet Feeder

## State Topics

| Topic                             | Payload       | Notes                                   |
| --------------------------------- | ------------- | --------------------------------------- |
| state/petfeeder/foodlevel         | 0-100         | Current food level in percentage (%)    |
| state/petfeeder/status            | Ready or Busy | Current pet feeder status               |
| state/petfeeder/dispenser/portion | 10-200        | Current pet feeder portion in grams (g) |

## Command Topics

| Topic                               | Payload | Notes                                       |
| ----------------------------------- | ------- | ------------------------------------------- |
| command/petfeeder/dispenser         | feed    | Dispenses food if the dispenser isn't busy. |
| command/petfeeder/dispenser/portion | 10-200  | Sets portion to dispense in grams.          |
| command/petfeeder/status            | status  | Force updates the food level state.         |
