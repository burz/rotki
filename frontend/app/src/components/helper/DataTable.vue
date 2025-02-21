<template>
  <v-data-table
    ref="tableRef"
    v-bind="$attrs"
    must-sort
    :sort-desc="sortDesc"
    :items="items"
    :item-class="itemClass"
    :headers="headers"
    :expanded="expanded"
    :footer-props="footerProps"
    :items-per-page="itemsPerPage"
    :hide-default-footer="hideDefaultFooter"
    v-on="$listeners"
    @update:items-per-page="onItemsPerPageChange($event)"
    @update:page="scrollToTop"
  >
    <!-- Pass on all named slots -->
    <slot v-for="slot in Object.keys($slots)" :slot="slot" :name="slot" />
    <!-- Pass on all scoped slots -->
    <template
      v-for="slot in Object.keys($scopedSlots)"
      :slot="slot"
      slot-scope="scope"
    >
      <slot :name="slot" v-bind="scope" />
    </template>

    <template
      v-if="!hideDefaultFooter"
      #top="{ pagination, options, updateOptions }"
    >
      <v-data-footer
        v-bind="footerProps"
        :pagination="pagination"
        :options="options"
        @update:options="updateOptions"
      />
      <v-divider />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, toRefs } from '@vue/composition-api';
import { get, useElementBounding } from '@vueuse/core';
import { DataTableHeader } from 'vuetify';
import { setupSettings } from '@/composables/settings';
import { footerProps } from '@/config/datatable.common';
import { ITEMS_PER_PAGE } from '@/types/frontend-settings';

export default defineComponent({
  name: 'DataTable',
  props: {
    sortDesc: { required: false, type: Boolean, default: true },
    items: { required: true, type: Array },
    headers: { required: true, type: Array as PropType<DataTableHeader[]> },
    expanded: { required: false, type: Array, default: () => [] },
    itemClass: { required: false, type: [String, Function], default: () => '' },
    hideDefaultFooter: { required: false, type: Boolean, default: false },
    container: { required: false, type: HTMLDivElement, default: () => null }
  },
  setup(props) {
    const { itemsPerPage, updateSetting } = setupSettings();
    const { container } = toRefs(props);

    const tableRef = ref<any>(null);

    const onItemsPerPageChange = async (newValue: number) => {
      await updateSetting({
        [ITEMS_PER_PAGE]: newValue
      });
    };

    const { top } = useElementBounding(tableRef);
    const { top: containerTop } = useElementBounding(container);

    const scrollToTop = () => {
      const wrapper = get(container) ?? document.body;
      const table = get(tableRef);

      if (!table || !wrapper) return;

      wrapper.scrollTop =
        get(top) +
        wrapper.scrollTop -
        (get(container) ? get(containerTop) : 64) -
        table.$el.scrollTop;
    };

    return {
      tableRef,
      itemsPerPage,
      footerProps,
      onItemsPerPageChange,
      scrollToTop
    };
  }
});
</script>

<style scoped lang="scss">
/* stylelint-disable selector-class-pattern,selector-nested-pattern,no-descending-specificity */

::v-deep {
  .v-data-table {
    &__expanded {
      &__content {
        background-color: var(--v-rotki-light-grey-base) !important;
        box-shadow: none !important;
      }
    }

    &--mobile {
      .v-data-table {
        &__wrapper {
          tbody {
            .v-data-table__expanded__content,
            .table-expand-container {
              height: auto !important;
              display: block;
            }
          }
        }
      }
    }
  }
}

.theme {
  &--dark {
    ::v-deep {
      .v-data-table {
        &__expanded {
          &__content {
            background-color: var(--v-dark-lighten1) !important;
          }
        }
      }
    }
  }
}
/* stylelint-enable selector-class-pattern,selector-nested-pattern,no-descending-specificity */
</style>
