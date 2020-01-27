# mtgml-resources
MTGML serverless api resources

## Backend repo deployment order
Uses SEED deployment manager
1. **mtgml-resources**
  - dev
  - prod
  - **service deployment order**
    1. storage & database
    2. auth
2. **mtgml-global-resources**
  - prod (only)
  - **service deployment order**
    1. database & search
3. **mtgml-api**
  - dev
  - prod
  - **service deployment order**
    1. decks
    2. payment
4. **mtgml-background-jobs**
  - prod (only)
  - **service deployment order**
    1. global-data

## Frontend repo deployment order
Uses Netlify deployment manager
1. **mtgml-frontend**
