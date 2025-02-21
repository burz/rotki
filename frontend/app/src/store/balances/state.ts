import { BalanceState } from '@/store/balances/types';

export const defaultState = (): BalanceState => ({
  eth: {},
  eth2: {},
  ksm: {},
  dot: {},
  avax: {},
  btc: {
    standalone: {},
    xpubs: []
  },
  bch: {
    standalone: {},
    xpubs: []
  },
  totals: {},
  liabilities: {},
  usdToFiatExchangeRates: {},
  connectedExchanges: [],
  exchangeBalances: {},
  ethAccounts: [],
  ksmAccounts: [],
  dotAccounts: [],
  avaxAccounts: [],
  btcAccounts: {
    standalone: [],
    xpubs: []
  },
  bchAccounts: {
    standalone: [],
    xpubs: []
  },
  eth2Validators: {
    entries: [],
    entriesLimit: 0,
    entriesFound: 0
  },
  manualBalances: [],
  manualLiabilities: [],
  manualBalanceByLocation: {},
  prices: {},
  loopringBalances: {},
  nonFungibleBalances: {}
});

export const state: BalanceState = defaultState();
