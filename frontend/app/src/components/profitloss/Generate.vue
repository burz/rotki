<template>
  <v-form v-model="valid">
    <card>
      <template #title>
        {{ $t('generate.title') }}
      </template>
      <template #details>
        <v-tooltip top>
          <template #activator="{ on, attrs }">
            <v-btn
              text
              fab
              depressed
              v-bind="attrs"
              to="/settings/accounting"
              v-on="on"
            >
              <v-icon color="primary">mdi-cog</v-icon>
            </v-btn>
          </template>
          <span>{{ $t('profit_loss_report.settings_tooltip') }}</span>
        </v-tooltip>
      </template>
      <range-selector v-model="range" />
      <template #buttons>
        <v-row no-gutters>
          <v-col>
            <v-btn
              color="primary"
              class="px-8"
              large
              depressed
              block
              :disabled="!valid"
              @click="generate()"
            >
              <v-icon class="mr-2">mdi-file-chart</v-icon>
              {{ $t('generate.generate') }}
            </v-btn>
          </v-col>
          <v-col cols="auto">
            <v-menu v-if="isDevelopment" offset-y left>
              <template #activator="{ on }">
                <v-btn
                  color="warning"
                  depressed
                  large
                  class="px-4 ml-4"
                  v-on="on"
                >
                  <v-icon class="mr-2">mdi-wrench</v-icon>
                  {{ $t('profit_loss_reports.debug.title') }}
                </v-btn>
              </template>
              <v-list>
                <v-list-item link @click="exportReportData">
                  <v-list-item-title>
                    <div class="d-flex align-center">
                      <v-icon class="mr-2">mdi-export</v-icon>
                      <span>
                        {{ $t('profit_loss_reports.debug.export_data') }}
                      </span>
                    </div>
                  </v-list-item-title>
                </v-list-item>
                <v-list-item link @click="importReportData">
                  <v-list-item-title>
                    <div class="d-flex align-center">
                      <v-icon class="mr-2">mdi-import</v-icon>
                      <span>
                        {{ $t('profit_loss_reports.debug.import_data') }}
                      </span>
                    </div>
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-btn
              v-else
              color="warning"
              depressed
              large
              class="px-4 ml-4"
              @click="exportReportData"
            >
              <v-icon class="mr-2">mdi-export</v-icon>
              {{ $t('profit_loss_reports.debug.export_data') }}
            </v-btn>
          </v-col>
        </v-row>
      </template>
    </card>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from '@vue/composition-api';
import { get } from '@vueuse/core';
import RangeSelector from '@/components/helper/date/RangeSelector.vue';
import { convertToTimestamp } from '@/utils/date';

export default defineComponent({
  name: 'Generate',
  components: {
    RangeSelector
  },
  emits: ['generate'],
  setup(_, { emit }) {
    const range = ref({ start: '', end: '' });
    const valid = ref<boolean>(false);

    const startTimestamp = computed<number>(() => {
      return convertToTimestamp(get(range).start);
    });

    const endTimestamp = computed<number>(() => {
      return convertToTimestamp(get(range).end);
    });

    const generate = () => {
      emit('generate', {
        start: get(startTimestamp),
        end: get(endTimestamp)
      });
    };

    const exportReportData = () => {
      emit('export-data', {
        start: get(startTimestamp),
        end: get(endTimestamp)
      });
    };

    const importReportData = () => {
      emit('import-data');
    };

    const isDevelopment = process.env.NODE_ENV === 'development';

    return {
      isDevelopment,
      range,
      valid,
      generate,
      exportReportData,
      importReportData
    };
  }
});
</script>
