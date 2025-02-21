<template>
  <stat-card
    v-if="!summary.balanceUsd"
    :title="summary.protocol.name"
    :protocol-icon="icon"
    bordered
    :class="$style.overview"
  >
    <div v-if="summary.liabilities">
      <span
        class="text-subtitle-1 font-weight-bold pb-2 d-flex flex-row justify-space-between"
      >
        {{ $t('overview.stat_card.headers.borrowing') }}
        <v-btn :to="summary.liabilitiesUrl" icon small color="primary">
          <v-icon small color="primary">mdi-launch</v-icon>
        </v-btn>
      </span>
      <info-row
        :title="$t('overview.stat_card.content.labels.total_collateral')"
        fiat
        :value="summary.totalCollateralUsd"
      />
      <info-row
        :title="$t('overview.stat_card.content.labels.total_debt')"
        fiat
        :value="summary.totalDebtUsd"
      />
      <v-divider class="my-4" />
    </div>
    <div v-if="summary.deposits">
      <div
        class="pb-2 d-flex flex-row justify-space-between text-subtitle-1 font-weight-medium"
      >
        {{ $t('overview.stat_card.headers.lending') }}
        <v-btn
          v-if="summary.depositsUrl"
          :to="summary.depositsUrl"
          icon
          small
          color="primary"
        >
          <v-icon small color="primary">mdi-launch</v-icon>
        </v-btn>
      </div>
      <info-row
        :title="$t('overview.stat_card.content.labels.total_deposited')"
        fiat
        :value="summary.totalLendingDepositUsd"
      />
    </div>
  </stat-card>
  <stat-card
    v-else
    bordered
    :title="summary.protocol.name"
    :protocol-icon="icon"
    :class="$style.overview"
  >
    <span class="text-subtitle-1 font-weight-bold pb-2">
      {{ summary.tokenInfo.tokenName }}
    </span>
    <info-row
      :title="$t('overview.stat_card.content.labels.balance')"
      fiat
      :value="summary.balanceUsd"
    />
    <v-divider class="my-4" />
    <v-dialog v-model="details" scrollable max-width="450px">
      <template #activator="{ on, attrs }">
        <v-btn small v-bind="attrs" block text class="justify-end" v-on="on">
          {{ $t('overview.stat_card.buttons.details') }}
          <v-icon color="primary" right>mdi-launch</v-icon>
        </v-btn>
      </template>
      <v-card>
        <v-card-title class="mb-2">
          <v-img
            aspect-ratio="1"
            :src="icon"
            max-width="32px"
            max-height="32px"
            contain
          />
          <span class="ml-2">
            {{ summary.protocol.name }}
          </span>
        </v-card-title>
        <v-card-subtitle>
          {{ $t('overview.details_dialog.subtitle') }}
        </v-card-subtitle>
        <v-card-text :class="$style.details">
          <div v-for="(asset, index) in assets" :key="index">
            <defi-asset :asset="asset" />
            <v-divider />
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </stat-card>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
  toRefs
} from '@vue/composition-api';
import { get } from '@vueuse/core';
import DefiAsset from '@/components/defi/DefiAsset.vue';
import InfoRow from '@/components/defi/display/InfoRow.vue';
import StatCard from '@/components/display/StatCard.vue';
import { DefiProtocolSummary } from '@/store/defi/types';

export default defineComponent({
  name: 'Overview',
  components: { DefiAsset, StatCard, InfoRow },
  props: {
    summary: {
      required: true,
      type: Object as PropType<DefiProtocolSummary>
    }
  },
  setup(props) {
    const details = ref(false);
    const { summary } = toRefs(props);
    const icon = computed(() => {
      const { protocol } = get(summary);
      if (!protocol.icon) {
        return '';
      }
      return `/assets/images/defi/${protocol.icon}`;
    });

    const assets = computed(() => {
      const { assets } = get(summary);
      return assets.sort(
        (
          { balance: { usdValue } },
          { balance: { usdValue: otherUsdValue } }
        ) => {
          if (usdValue.eq(otherUsdValue)) {
            return 0;
          }
          return usdValue.gt(otherUsdValue) ? -1 : 1;
        }
      );
    });

    return {
      details,
      icon,
      assets
    };
  }
});
</script>

<style module lang="scss">
.overview {
  min-height: 250px !important;
  min-width: 300px;
}

.details {
  height: 300px;
}
</style>
