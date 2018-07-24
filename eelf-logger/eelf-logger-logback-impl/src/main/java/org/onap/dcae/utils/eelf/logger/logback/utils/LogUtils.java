/*
 * ================================================================================
 * Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
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
 * ECOMP is a trademark and service mark of AT&T Intellectual Property.
 */

package org.onap.dcae.utils.eelf.logger.logback.utils;

import ch.qos.logback.core.CoreConstants;
import org.onap.dcae.utils.eelf.logger.api.info.AppLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.info.NagiosAlertLevel;
import org.onap.dcae.utils.eelf.logger.api.info.RequestIdLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.RequestStatusCode;
import org.onap.dcae.utils.eelf.logger.api.spec.AppLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.AuditLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.MetricLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults;
import org.onap.dcae.utils.eelf.logger.logback.resolver.CompositePropertyResolver;
import org.onap.dcae.utils.eelf.logger.logback.resolver.EnvironmentPropertyResolver;
import org.onap.dcae.utils.eelf.logger.logback.resolver.SystemPropertyResolver;
import org.onap.dcae.utils.eelf.logger.model.info.AppLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.CodeLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.MessageLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.RequestIdLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.RequestTimingLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.AppLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.AuditLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.DebugLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.ErrorLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.MetricLogSpecImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.OptionalLogSpecImpl;
import org.slf4j.Logger;
import org.slf4j.Marker;
import org.slf4j.MarkerFactory;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;
import java.util.UUID;



/**
 * Contains various logging utility methods
 *
 * @author Rajiv Singla
 */
public abstract class LogUtils {

    private static final String LOG_MESSAGE_DELIMITER = "|";
    private static final String DATE_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSZ";
    private static final String DATE_TIMEZONE = "UTC";
    // property resolver which looks up system property and the environment properties
    private static final CompositePropertyResolver COMPOSITE_PROPERTY_RESOLVER =
            new CompositePropertyResolver(new SystemPropertyResolver(), new EnvironmentPropertyResolver());

    // Custom MDC Map Keys
    public static final String APP_LOG_SPEC_KEY = "APP_LOG_SPEC";
    public static final String AUDIT_LOG_SPEC_KEY = "AUDIT_LOG_SPEC";
    public static final String METRIC_LOG_SPEC_KEY = "METRIC_LOG_SPEC";
    public static final String ERROR_LOG_SPEC_KEY = "ERROR_LOG_SPEC";
    public static final String DEBUG_LOG_SPEC_KEY = "DEBUG_LOG_SPEC";
    public static final String OPTIONAL_LOG_SPEC_KEY = "OPTIONAL_LOG_SPEC";
    public static final String LOG_LEVEL_CATEGORY_KEY = "LOG_LEVEL_CATEGORY";
    public static final String LOGGER_CLASS_KEY = "LOGGER_CLASS_KEY";

    // markers
    public static final Marker AUDIT_LOG_MARKER = MarkerFactory.getMarker("AUDIT_LOG");
    public static final Marker METRIC_LOG_MARKER = MarkerFactory.getMarker("METRIC_LOG");
    public static final Marker ERROR_LOG_MARKER = MarkerFactory.getMarker("ERROR_LOG");
    public static final Marker DEBUG_LOG_MARKER = MarkerFactory.getMarker("DEBUG_LOG");


    public static final Map<String, Object> CUSTOM_MDC_MAP = new ThreadLocal<Map<String, Object>>() {
        @Override
        protected Map<String, Object> initialValue() {
            return new HashMap<>();
        }
    }.get();

    public static final ThreadLocal<SimpleDateFormat> SIMPLE_DATE_FORMAT = new ThreadLocal<SimpleDateFormat>() {
        @Override
        protected SimpleDateFormat initialValue() {
            final SimpleDateFormat simpleDateFormat = new SimpleDateFormat(DATE_FORMAT);
            simpleDateFormat.setTimeZone(TimeZone.getTimeZone(DATE_TIMEZONE));
            return simpleDateFormat;
        }
    };


    private LogUtils() {
        // private constructor
    }


    /**
     * Logs eomp message with normalized log level category
     *
     * @param logLevelCategory ecomp log level category
     * @param logger logback logger
     * @param marker logback marker
     * @param message log message
     * @param args log message arguments for interpolation
     */
    public static void logWithLogLevel(final LogLevelCategory logLevelCategory,
                                       final Logger logger, final Marker marker,
                                       final String message, final String... args) {
        switch (logLevelCategory) {
            case DEBUG:
                logger.debug(marker, message, args);
                break;
            case INFO:
                logger.info(marker, message, args);
                break;
            case WARN:
                logger.warn(marker, message, args);
                break;
            default:
                // fatal log level is treated as error also as logback does not have fatal level
                logger.error(marker, message, args);
        }
    }


    /**
     * Returns value for {@link AppLogSpec}. If no {@link AppLogSpec} is defined a default app log spec is passed
     *
     * @return app log spec
     */
    public static AppLogSpec getAppLogSpec() {
        final AppLogSpec appLogSpec = getCustomMapValue(APP_LOG_SPEC_KEY, AppLogSpec.class);
        return appLogSpec == null ? new AppLogSpecImpl(EELFLoggerDefaults.DEFAULT_APP_LOG_INFO) : appLogSpec;
    }

    /**
     * Populate default values of {@link OptionalLogSpec} if not present
     *
     * @param loggerClass logger class
     * @param logLevelCategory log level category
     *
     * @return optional log spec with default values if not present
     */
    public static OptionalLogSpec getOptionalLogSpec(final Class<?> loggerClass, final LogLevelCategory
            logLevelCategory) {

        OptionalLogSpecImpl optionalLogSpec =
                getCustomMapValue(OPTIONAL_LOG_SPEC_KEY, OptionalLogSpecImpl.class);

        if (optionalLogSpec != null) {
            // if message log info is empty populate default values
            if (optionalLogSpec.getMessageLogInfo() == null ||
                    optionalLogSpec.getCreationTimestamp() == null && optionalLogSpec.getAlertSeverity() == null &&
                            optionalLogSpec.getStatusCode() == null) {
                optionalLogSpec = optionalLogSpec.withMessageLogInfo(createDefaultMessageLogInfo(logLevelCategory));
            }
            // if code log info is empty populate default values
            if (optionalLogSpec.getCodeLogInfo() == null ||
                    optionalLogSpec.getClassName() == null && optionalLogSpec.getThreadId() == null) {
                optionalLogSpec = optionalLogSpec.withCodeLogInfo(createDefaultCodeLogInfo(loggerClass));
            }
            // if custom fields log info is empty populate default values
            if (optionalLogSpec.getCustomFieldsLogInfo() == null) {
                optionalLogSpec =
                        optionalLogSpec.withCustomFieldsLogInfo(EELFLoggerDefaults.DEFAULT_CUSTOM_FIELDS_LOG_INFO);
            }
            // if misc fields log info is empty populate default values
            if (optionalLogSpec.getMiscLogInfo() == null) {
                optionalLogSpec = optionalLogSpec.withMiscLogInfo(EELFLoggerDefaults.DEFAULT_MISC_LOG_INFO);
            }
        } else {
            // optional log spec is null so create new optional log spec
            optionalLogSpec = createDefaultOptionalLogSpec(loggerClass, logLevelCategory);
        }

        return optionalLogSpec;
    }


    /**
     * Formats given date in ISO 8601 format
     *
     * @param date Date object
     *
     * @return formatted date string
     */
    public static String formatDate(final Date date) {
        if (date == null) {
            return "";
        }
        return SIMPLE_DATE_FORMAT.get().format(date);
    }

    /**
     * Creates log message string
     *
     * @param logValues log message values
     *
     * @return log message string
     */
    public static String createLogMessageString(final String[] logValues) {
        final StringBuffer stringBuffer = new StringBuffer(512);
        for (int i = 0; i < logValues.length; i++) {
            final String logValue = logValues[i];
            stringBuffer.append(logValue != null ? logValue : "");
            if (i != logValues.length - 1) {
                stringBuffer.append(LOG_MESSAGE_DELIMITER);
            }
        }
        stringBuffer.append(CoreConstants.LINE_SEPARATOR);
        return stringBuffer.toString();
    }

    /**
     * Gets custom MDC value from Custom MDC Map for give key. Returns null if no value can be found
     *
     * @param key MDC Map key
     * @param clazz expected value class type
     * @param <T> class type
     *
     * @return value inside Custom MDC Map
     */
    private static <T> T getCustomMapValue(final String key, final Class<T> clazz) {
        final Object value = CUSTOM_MDC_MAP.get(key);
        if (value != null) {
            return clazz.cast(value);
        }
        return null;
    }


    /**
     * Get current Metric log spec from the custom MDC map and populates default values if not present
     *
     * @return Metric log spec
     */
    public static MetricLogSpec getMetricLogSpec() {
        MetricLogSpecImpl metricLogSpec = getCustomMapValue(METRIC_LOG_SPEC_KEY, MetricLogSpecImpl.class);

        if (metricLogSpec != null) {
            if (metricLogSpec.getRequestIdLogInfo() == null || metricLogSpec.getRequestId() == null) {
                metricLogSpec = metricLogSpec.withRequestIdLogInfo(createNewRequestIdLogInfo());
            }
            if (metricLogSpec.getServiceLogInfo() == null) {
                metricLogSpec = metricLogSpec.withServiceLogInfo(EELFLoggerDefaults.DEFAULT_SERVICE_LOG_INFO);
            }
            if (metricLogSpec.getRequestTimingLogInfo() == null || metricLogSpec.getBeginTimestamp() == null ||
                    metricLogSpec.getEndTimestamp() == null) {
                metricLogSpec =
                        metricLogSpec.withRequestTimingLogInfo(EELFLoggerDefaults.DEFAULT_REQUEST_TIMING_LOG_INFO);
            }
            if (metricLogSpec.getResponseLogInfo() == null) {
                metricLogSpec = metricLogSpec.withResponseLogInfo(EELFLoggerDefaults.DEFAULT_RESPONSE_LOG_INFO);
            }
            final Date beginTimestamp = metricLogSpec.getBeginTimestamp();
            final Date endTimestamp = metricLogSpec.getEndTimestamp();
            final Long elapsedTime = metricLogSpec.getElapsedTime();
            if (endTimestamp != null && beginTimestamp != null && elapsedTime == null) {
                final RequestTimingLogInfoImpl requestTimingLogInfo =
                        new RequestTimingLogInfoImpl(beginTimestamp, endTimestamp,
                                endTimestamp.getTime() - beginTimestamp.getTime());
                metricLogSpec = metricLogSpec.withRequestTimingLogInfo(requestTimingLogInfo);
            }
            if (metricLogSpec.getTargetServiceLogInfo() == null) {
                metricLogSpec =
                        metricLogSpec.withTargetServiceLogInfo(EELFLoggerDefaults.DEFAULT_TARGET_SERVICE_LOG_INFO);
            }
        } else {
            throw new IllegalArgumentException("Metric Log Spec must not be null");
        }

        return metricLogSpec;
    }

    /**
     * Get current Debug log spec from the custom MDC map and populates default values if not present
     *
     * @return Debug log spec
     */
    public static DebugLogSpec getDebugLogSpec() {
        final DebugLogSpecImpl debugLogSpec = getCustomMapValue(DEBUG_LOG_SPEC_KEY, DebugLogSpecImpl.class);
        if (debugLogSpec == null || debugLogSpec.getRequestIdLogInfo() == null || debugLogSpec.getRequestId() == null) {
            return new DebugLogSpecImpl(createNewRequestIdLogInfo());
        }
        return debugLogSpec;
    }

    /**
     * Get current Error log spec from the custom MDC map and populates default values if not present
     *
     * @return Error log spec
     */
    public static ErrorLogSpec getErrorLogSpec() {
        ErrorLogSpecImpl errorLogSpec = getCustomMapValue(ERROR_LOG_SPEC_KEY, ErrorLogSpecImpl.class);
        if (errorLogSpec != null) {

            if (errorLogSpec.getRequestIdLogInfo() == null || errorLogSpec.getRequestId() == null) {
                errorLogSpec = errorLogSpec.withRequestIdLogInfo(createNewRequestIdLogInfo());
            }
            if (errorLogSpec.getServiceLogInfo() == null) {
                errorLogSpec = errorLogSpec.withServiceLogInfo(EELFLoggerDefaults.DEFAULT_SERVICE_LOG_INFO);
            }
            if (errorLogSpec.getTargetServiceLogInfo() == null) {
                errorLogSpec =
                        errorLogSpec.withTargetServiceLogInfo(EELFLoggerDefaults.DEFAULT_TARGET_SERVICE_LOG_INFO);
            }
            if (errorLogSpec.getErrorLogInfo() == null) {
                errorLogSpec = errorLogSpec.withErrorLogInfo(EELFLoggerDefaults.DEFAULT_ERROR_LOG_INFO);
            }

        } else {
            throw new IllegalArgumentException("Error Log Spec cannot be null");
        }
        return errorLogSpec;
    }


    /**
     * Get current Audit log spec from the custom MDC map and populates default values if not present
     *
     * @return Audit log spec
     */
    public static AuditLogSpec getAuditLogSpec() {
        AuditLogSpecImpl auditLogSpec = getCustomMapValue(AUDIT_LOG_SPEC_KEY, AuditLogSpecImpl.class);
        if (auditLogSpec != null) {
            if (auditLogSpec.getServiceLogInfo() == null) {
                auditLogSpec = auditLogSpec.withServiceLogInfo(EELFLoggerDefaults.DEFAULT_SERVICE_LOG_INFO);
            }
            if (auditLogSpec.getRequestIdLogInfo() == null || auditLogSpec.getRequestId() == null) {
                auditLogSpec = auditLogSpec.withRequestIdLogInfo(createNewRequestIdLogInfo());
            }
            if (auditLogSpec.getResponseLogInfo() == null) {
                auditLogSpec = auditLogSpec.withResponseLogInfo(EELFLoggerDefaults.DEFAULT_RESPONSE_LOG_INFO);
            }

            if (auditLogSpec.getRequestTimingLogInfo() == null || auditLogSpec.getBeginTimestamp() == null ||
                    auditLogSpec.getEndTimestamp() == null) {
                auditLogSpec =
                        auditLogSpec.withRequestTimingLogInfo(EELFLoggerDefaults.DEFAULT_REQUEST_TIMING_LOG_INFO);
            }
            final Date beginTimestamp = auditLogSpec.getBeginTimestamp();
            final Date endTimestamp = auditLogSpec.getEndTimestamp();
            final Long elapsedTime = auditLogSpec.getElapsedTime();
            if (endTimestamp != null && beginTimestamp != null && elapsedTime == null) {
                final RequestTimingLogInfoImpl requestTimingLogInfo =
                        new RequestTimingLogInfoImpl(beginTimestamp, endTimestamp,
                                endTimestamp.getTime() - beginTimestamp.getTime());
                auditLogSpec = auditLogSpec.withRequestTimingLogInfo(requestTimingLogInfo);
            }

        } else {
            throw new IllegalArgumentException("Audit Log Spec cannot be null");
        }

        return auditLogSpec;
    }


    private static RequestIdLogInfo createNewRequestIdLogInfo() {
        return new RequestIdLogInfoImpl(UUID.randomUUID().toString());
    }

    /**
     * Return Log Level Category from MDC Map
     *
     * @return log level category
     */
    public static Class<?> getLoggerClass() {
        final Class<?> loggerClass = getCustomMapValue(LOGGER_CLASS_KEY, Class.class);
        // logger class must always be non null
        if (loggerClass != null) {
            return loggerClass;
        }
        return LogUtils.class.getClass();
    }


    /**
     * Return Log Level Category from MDC Map
     *
     * @return log level category
     */
    public static LogLevelCategory getLogLevelCategory() {
        final LogLevelCategory logLevelCategory = getCustomMapValue(LOG_LEVEL_CATEGORY_KEY, LogLevelCategory.class);
        if (logLevelCategory != null) {
            return logLevelCategory;
        }
        return LogLevelCategory.ERROR;
    }

    /**
     * Creates Default Optional Log spec
     *
     * @param loggerClass logger class name
     * @param logLevelCategory Log leve category
     *
     * @return default optional log spec
     */
    private static OptionalLogSpecImpl createDefaultOptionalLogSpec(final Class<?> loggerClass,
                                                                    final LogLevelCategory logLevelCategory) {
        return new OptionalLogSpecImpl(createDefaultMessageLogInfo(logLevelCategory),
                createDefaultCodeLogInfo(loggerClass), EELFLoggerDefaults.DEFAULT_CUSTOM_FIELDS_LOG_INFO,
                EELFLoggerDefaults.DEFAULT_MISC_LOG_INFO);
    }


    /**
     * Creates Default Code Log Info
     *
     * @param loggerClass logger class name
     *
     * @return default code log info
     */
    private static CodeLogInfoImpl createDefaultCodeLogInfo(final Class<?> loggerClass) {
        // thread id can be extracted from the framework
        return new CodeLogInfoImpl(null, loggerClass != null ? loggerClass.getName() : "");
    }


    /**
     * Creates Default Message Log Info
     *
     * @param logLevelCategory Log leve category
     *
     * @return default message log info
     */
    private static MessageLogInfoImpl createDefaultMessageLogInfo(final LogLevelCategory logLevelCategory) {
        return new MessageLogInfoImpl(new Date(),
                getStatusCode(logLevelCategory),
                getNagiosAlertLevel(logLevelCategory));
    }


    /**
     * Creates Default App Log Spec
     *
     * @return default APP log Spec
     */
    public static AppLogInfoImpl createDefaultAppLogInfo() {
        final String serviceInstanceId =
                resolveProperty(null, AppLogInfo.Defaults.DEFAULT_SERVICE_INSTANCE_ID,
                        "SERVICE_NAME", "ServiceInstanceId", "SERVICE_INSTANCE_ID");
        final String instanceUUID =
                resolveProperty(null, AppLogInfo.Defaults.DEFAULT_INSTANCE_UUID,
                        "InstanceUUID", "INSTANCE_UUID");
        final String virtualServerName =
                resolveProperty(null, AppLogInfo.Defaults.DEFAULT_VIRTUAL_SERVER_NAME,
                        "VirtualServerName", "VIRTUAL_SERVER_NAME");
        final String serverIPAddress = getHostIPAddress() != null ?
                getHostIPAddress() : AppLogInfo.Defaults.DEFAULT_SERVER_IP_ADDRESS;
        final String serverFQDN = getHostName() != null ? getHostName() : AppLogInfo.Defaults.DEFAULT_SERVER_FQDN;
        return new AppLogInfoImpl(serviceInstanceId, instanceUUID, virtualServerName, serverIPAddress, serverFQDN);
    }


    /**
     * Returns status code based on log level category
     *
     * @param logLevelCategory log level category
     *
     * @return request status code as string based on log level category
     */
    private static RequestStatusCode getStatusCode(final LogLevelCategory logLevelCategory) {
        if (logLevelCategory == LogLevelCategory.DEBUG || logLevelCategory == LogLevelCategory.INFO ||
                logLevelCategory == LogLevelCategory.WARN) {
            return RequestStatusCode.COMPLETE;
        } else {
            return RequestStatusCode.ERROR;
        }
    }

    /**
     * Returns nagios Alert level based on log level category
     *
     * @param logLevelCategory log level category
     *
     * @return nagios alert level
     */
    private static NagiosAlertLevel getNagiosAlertLevel(final LogLevelCategory logLevelCategory) {
        switch (logLevelCategory) {
            case DEBUG:
                return NagiosAlertLevel.OK;
            case INFO:
                return NagiosAlertLevel.OK;
            case WARN:
                return NagiosAlertLevel.WARNING;
            case ERROR:
                return NagiosAlertLevel.CRITICAL;
            case FATAL:
                return NagiosAlertLevel.CRITICAL;
            default:
                return NagiosAlertLevel.UNKNOWN;
        }
    }

    /**
     * Resolves property value if not present
     *
     * @param userPassedValue user passed property value
     * @param defaultValue default value if no value is found after resolving the property
     * @param propertyNames property names
     *
     * @return resolved property value
     */
    private static String resolveProperty(
            final String userPassedValue, final String defaultValue, final String... propertyNames) {
        // if user passed is present return that value
        if (userPassedValue != null) {
            return userPassedValue;
        }
        // resolve it using composite resolver
        final String resolveProperty = resolveProperty(Arrays.asList(propertyNames));
        return resolveProperty != null ? resolveProperty : defaultValue;
    }

    /**
     * Resolves property values in different places
     *
     * @param propertyNames property Names
     *
     * @return property Value
     */
    private static String resolveProperty(final List<String> propertyNames) {
        return COMPOSITE_PROPERTY_RESOLVER.resolve(propertyNames);
    }


    /**
     * Determine host IP Address
     *
     * @return host ip address
     */
    private static String getHostIPAddress() {
        final InetAddress inetAddress = getInetAddress();
        if (inetAddress != null) {
            return inetAddress.getHostAddress();
        }
        return null;
    }

    /**
     * Determines fully qualified host name
     *
     * @return fully qualified host name
     */
    private static String getHostName() {
        final InetAddress inetAddress = getInetAddress();
        if (inetAddress != null) {
            return inetAddress.getCanonicalHostName();
        }
        return null;
    }

    /**
     * Fetches Inet Address
     *
     * @return Inet Address
     */
    private static InetAddress getInetAddress() {
        try {
            return InetAddress.getLocalHost();
        } catch (UnknownHostException e) {
            return null;
        }
    }


}
