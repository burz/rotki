<template>
  <card contained>
    <template #title>{{ $t('backend_settings.title') }}</template>
    <template #subtitle>{{ $t('backend_settings.subtitle') }}</template>

    <v-text-field
      v-model="userDataDirectory"
      :loading="!userDataDirectory"
      class="pt-2"
      outlined
      :disabled="!!fileConfig.dataDirectory || !userDataDirectory"
      persistent-hint
      :hint="
        !!fileConfig.dataDirectory
          ? $t('backend_settings.config_file_disabled')
          : $t('backend_settings.settings.data_directory.hint')
      "
      :label="$t('backend_settings.settings.data_directory.label')"
      readonly
      @click="selectDataDirectory"
    >
      <template #append>
        <v-btn icon :disabled="!userDataDirectory" @click="selectDataDirectory">
          <v-icon>mdi-folder</v-icon>
        </v-btn>
      </template>
    </v-text-field>

    <v-text-field
      v-model="userLogDirectory"
      :disabled="!!fileConfig.logDirectory"
      :persistent-hint="!!fileConfig.logDirectory"
      :hint="
        !!fileConfig.logDirectory
          ? $t('backend_settings.config_file_disabled')
          : null
      "
      outlined
      :label="$t('backend_settings.settings.log_directory.label')"
      readonly
      @click="selectLogsDirectory"
    >
      <template #append>
        <v-btn icon @click="selectLogsDirectory">
          <v-icon>mdi-folder</v-icon>
        </v-btn>
      </template>
    </v-text-field>

    <v-select
      v-model="loglevel"
      :items="levels"
      :disabled="!!fileConfig.loglevel"
      :label="$t('backend_settings.settings.log_level.label')"
      :persistent-hint="!!fileConfig.loglevel"
      :hint="
        !!fileConfig.loglevel
          ? $t('backend_settings.config_file_disabled')
          : null
      "
      outlined
    >
      <template #item="{ item }">
        <v-row align="center">
          <v-col cols="auto">
            <v-icon>{{ icon(item) }}</v-icon>
          </v-col>
          <v-col>{{ item.toLocaleLowerCase() }}</v-col>
        </v-row>
      </template>
      <template #selection="{ item }">
        <v-row align="center">
          <v-col cols="auto">
            <v-icon>{{ icon(item) }}</v-icon>
          </v-col>
          <v-col>{{ item.toLocaleLowerCase() }}</v-col>
        </v-row>
      </template>
    </v-select>

    <v-expansion-panels flat>
      <v-expansion-panel>
        <v-expansion-panel-header>
          {{ $t('backend_settings.advanced') }}
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-text-field
            v-model="maxLogSize"
            outlined
            :hint="
              !!fileConfig.maxSizeInMbAllLogs
                ? $t('backend_settings.config_file_disabled')
                : $t('backend_settings.max_log_size.hint')
            "
            :label="$t('backend_settings.max_log_size.label')"
            :disabled="fileConfig.maxSizeInMbAllLogs"
            :persistent-hint="!!fileConfig.maxSizeInMbAllLogs"
            clearable
            type="number"
          />
          <v-text-field
            v-model="maxLogFiles"
            outlined
            :hint="$t('backend_settings.max_log_files.hint')"
            :label="
              !!fileConfig.maxSizeInMbAllLogs
                ? $t('backend_settings.config_file_disabled')
                : $t('backend_settings.max_log_files.label')
            "
            :disabled="fileConfig.maxSizeInMbAllLogs"
            :persistent-hint="!!fileConfig.maxSizeInMbAllLogs"
            clearable
            type="number"
          />
          <v-text-field
            v-model="mainLoopSleep"
            outlined
            :hint="
              !!fileConfig.sleepSeconds
                ? $t('backend_settings.config_file_disabled')
                : $t('backend_settings.main_loop_sleep.hint')
            "
            :label="$t('backend_settings.main_loop_sleep.label')"
            :disabled="!!fileConfig.sleepSeconds"
            :persistent-hint="!!fileConfig.sleepSeconds"
            clearable
            type="number"
          />

          <v-checkbox
            v-model="logFromOtherModules"
            :label="$t('backend_settings.log_from_other_modules.label')"
            :disabled="!!fileConfig.logFromOtherModules"
            persistent-hint
            :hint="
              !!fileConfig.logFromOtherModules
                ? $t('backend_settings.config_file_disabled')
                : $t('backend_settings.log_from_other_modules.hint')
            "
          />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

    <template #buttons>
      <v-spacer />
      <v-btn depressed @click="dismiss()">
        {{ $t('backend_settings.actions.cancel') }}
      </v-btn>
      <v-btn depressed @click="confirmReset = true">
        {{ $t('backend_settings.actions.reset') }}
      </v-btn>
      <v-btn depressed color="primary" :disabled="!valid" @click="save()">
        {{ $t('backend_settings.actions.save') }}
      </v-btn>
    </template>
    <confirm-dialog
      v-if="confirmReset"
      :message="$t('backend_settings.confirm.message')"
      :display="confirmReset"
      :title="$t('backend_settings.confirm.title')"
      @confirm="reset"
      @cancel="confirmReset = false"
    />
  </card>
</template>

<script lang="ts">
import { mapState } from 'pinia';
import { Component, Emit, Mixins, Watch } from 'vue-property-decorator';
import ConfirmDialog from '@/components/dialogs/ConfirmDialog.vue';
import { BackendOptions } from '@/electron-main/ipc';
import BackendMixin from '@/mixins/backend-mixin';
import { useMainStore } from '@/store/store';
import { Writeable } from '@/types';
import { LogLevel } from '@/utils/log-level';

@Component({
  name: 'BackendSettings',
  components: { ConfirmDialog },
  computed: {
    ...mapState(useMainStore, ['dataDirectory'])
  }
})
export default class BackendSettings extends Mixins(BackendMixin) {
  dataDirectory!: string;
  userDataDirectory: string = '';
  userLogDirectory: string = '';
  logFromOtherModules: boolean = false;
  mainLoopSleep: string = '';
  maxLogSize: string = '';
  maxLogFiles: string = '';

  readonly levels = Object.values(LogLevel);
  selecting: boolean = false;
  confirmReset: boolean = false;

  @Emit()
  dismiss() {}

  get valid() {
    const newOptions = this.newUserOptions;
    const oldOptions = this.options;
    const newLogLevel = newOptions.loglevel ?? this.defaultLogLevel;
    const oldLogLevel = oldOptions.loglevel ?? this.defaultLogLevel;
    let updatedKeys = Object.keys(newOptions).filter(s => s !== 'loglevel');
    return updatedKeys.length > 0 || newLogLevel !== oldLogLevel;
  }

  get newUserOptions(): Partial<BackendOptions> {
    const options: Writeable<Partial<BackendOptions>> = {};
    if (this.loglevel !== this.defaultLogLevel) {
      options.loglevel = this.loglevel;
    }

    if (this.userLogDirectory !== this.defaultLogDirectory) {
      options.logDirectory = this.userLogDirectory;
    }

    if (this.mainLoopSleep) {
      const seconds = parseInt(this.mainLoopSleep);
      if (isFinite(seconds) && !isNaN(seconds)) {
        options.sleepSeconds = seconds;
      }
    }

    if (this.logFromOtherModules) {
      options.logFromOtherModules = true;
    }

    if (this.userDataDirectory !== this.dataDirectory) {
      options.dataDirectory = this.userDataDirectory;
    }

    if (this.maxLogFiles) {
      const files = parseInt(this.maxLogFiles);
      if (isFinite(files) && !isNaN(files)) {
        options.maxLogfilesNum = files;
      }
    }

    if (this.maxLogSize) {
      const mb = parseInt(this.maxLogSize);
      if (isFinite(mb) && !isNaN(mb)) {
        options.maxSizeInMbAllLogs = mb;
      }
    }

    return options;
  }

  icon(level: LogLevel): string {
    if (level === LogLevel.DEBUG) {
      return 'mdi-bug';
    } else if (level === LogLevel.INFO) {
      return 'mdi-information';
    } else if (level === LogLevel.WARNING) {
      return 'mdi-alert';
    } else if (level === LogLevel.ERROR) {
      return 'mdi-alert-circle';
    } else if (level === LogLevel.CRITICAL) {
      return 'mdi-alert-decagram';
    } else if (level === LogLevel.TRACE) {
      return 'mdi-magnify-scan';
    }
    throw new Error(`Invalid option: ${level}`);
  }

  @Watch('dataDirectory')
  onDataDirectoryChange() {
    this.userDataDirectory = this.options.dataDirectory ?? this.dataDirectory;
  }

  loaded() {
    this.userDataDirectory = this.options.dataDirectory ?? this.dataDirectory;
    this.userLogDirectory =
      this.options.logDirectory ?? this.defaultLogDirectory;
    this.loglevel = this.options.loglevel ?? this.defaultLogLevel;
    this.mainLoopSleep = this.options.sleepSeconds?.toString() ?? '';
    this.logFromOtherModules = this.options.logFromOtherModules ?? false;
    this.maxLogFiles = this.options.maxLogfilesNum?.toString() ?? '';
    this.maxLogSize = this.options.maxSizeInMbAllLogs?.toString() ?? '';
  }

  async save() {
    this.dismiss();
    await this.saveOptions(this.newUserOptions);
  }

  async selectLogsDirectory() {
    if (this.selecting) {
      return;
    }
    this.selecting = true;
    try {
      const directory = await this.$interop.openDirectory(
        this.$t('backend_settings.log_directory.select').toString()
      );
      if (directory) {
        this.userLogDirectory = directory;
      }
    } finally {
      this.selecting = false;
    }
  }

  async selectDataDirectory() {
    if (this.selecting) {
      return;
    }
    this.selecting = true;
    try {
      const directory = await this.$interop.openDirectory(
        this.$t('backend_settings.data_directory.select').toString()
      );
      if (directory) {
        this.userDataDirectory = directory;
      }
    } finally {
      this.selecting = false;
    }
  }

  async reset() {
    this.confirmReset = false;
    this.dismiss();
    await this.resetOptions();
  }
}
</script>

<style scoped lang="scss">
::v-deep {
  .v-expansion-panel-content {
    &__wrap {
      padding: 0 0 16px;
    }
  }

  .v-expansion-panel-header {
    padding: 16px 0;
  }
}
</style>
