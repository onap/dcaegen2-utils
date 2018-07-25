/*
 * ================================================================================
 * Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END=========================================================
 *
 */

package org.onap.dcae.utils.eelf.logger.logback.listener;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.spi.LoggerContextListener;
import ch.qos.logback.core.Context;
import ch.qos.logback.core.spi.ContextAwareBase;
import ch.qos.logback.core.spi.LifeCycle;
import ch.qos.logback.core.status.InfoStatus;
import ch.qos.logback.core.status.WarnStatus;
import org.onap.dcae.utils.eelf.logger.api.info.AppLogInfo;
import org.onap.dcae.utils.eelf.logger.model.spec.AppLogSpecImpl;


import java.io.File;

import static org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults.DEFAULT_APP_LOG_INFO;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.APP_LOG_SPEC_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.CUSTOM_MDC_MAP;


/**
 * Logback Startup Listener is used to inject {@link AppLogInfo}
 *
 * @author Rajiv Singla
 */
public class LogbackStartupListener extends ContextAwareBase implements LoggerContextListener, LifeCycle {

    private static final String APP_LOG_INFO_KEY_IN_CONTEXT = "APP_LOG_INFO";
    private static final String CONTEXT_COMPONENT_NAME_PROPERTY_KEY = "componentName";
    private static final String CONTEXT_MODIFY_WINDOWS_LOG_PATH_PROPERTY_KEY = "modifyLogPathInWindows";
    private static final String CONTEXT_LOG_DIRECTORY_PROPERTY_KEY = "logDirectory";
    private static final String CONTEXT_DEBUG_LOG_DIRECTORY_PROPERTY_KEY = "debugLogDirectory";
    private static final String CONTEXT_APPEND_DIRECTORY_PROPERTY_KEY = "appendDirectory";

    private boolean started = false;

    @Override
    public boolean isResetResistant() {
        return true;
    }

    @Override
    public void onStart(final LoggerContext context) {

    }

    @Override
    public void onReset(final LoggerContext context) {

    }

    @Override
    public void onStop(final LoggerContext context) {

    }

    @Override
    public void onLevelChange(final Logger logger, final Level level) {

    }

    @Override
    public void start() {
        if (started) {
            return;
        }

        Context context = getContext();

        CUSTOM_MDC_MAP.put(APP_LOG_SPEC_KEY, new AppLogSpecImpl(DEFAULT_APP_LOG_INFO));
        context.putObject(APP_LOG_INFO_KEY_IN_CONTEXT, DEFAULT_APP_LOG_INFO);
        context.getStatusManager().add(new InfoStatus("Initialized APP LOG INFO", DEFAULT_APP_LOG_INFO));

        // if Component name is not set derive from jar file name
        if (context.getProperty(CONTEXT_COMPONENT_NAME_PROPERTY_KEY) == null) {
            final String appName =
                    new File(getClass().getProtectionDomain().getCodeSource().getLocation().getPath()).getName();
            context.putProperty(CONTEXT_COMPONENT_NAME_PROPERTY_KEY, appName);
            context.getStatusManager().add(new WarnStatus(
                    "No componentName Property found. Deriving it from jar name", appName));
        }

        // if modify windows log path is enabled - then append target before log directories
        if (context.getProperty(CONTEXT_MODIFY_WINDOWS_LOG_PATH_PROPERTY_KEY).equalsIgnoreCase("true")) {
            final String os = System.getProperty("os.name");
            if (os != null && os.startsWith("Windows")) {
                final String logDirectory = context.getProperty(CONTEXT_LOG_DIRECTORY_PROPERTY_KEY);
                final String debugLogDirectory = context.getProperty(CONTEXT_DEBUG_LOG_DIRECTORY_PROPERTY_KEY);
                final String appendDir = context.getProperty(CONTEXT_APPEND_DIRECTORY_PROPERTY_KEY);
                context.putProperty(CONTEXT_LOG_DIRECTORY_PROPERTY_KEY, appendDir + "/" + logDirectory);
                context.putProperty(CONTEXT_DEBUG_LOG_DIRECTORY_PROPERTY_KEY, appendDir + "/" + debugLogDirectory);
            }
        }

        started = true;
    }

    @Override
    public void stop() {

    }

    @Override
    public boolean isStarted() {
        return started;
    }
}
